from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Genre, Album, Song
import httplib2
import json
import pprint

pp = pprint.PrettyPrinter(indent=4)

engine = create_engine('sqlite:///vinyls.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# test
# hiphop = Genre(name="Hip Hop")
# session.add(hiphop)
# session.commit()
#
# album1 = Album(genre=hiphop,
#                title="Album 1",
#                artist="Blabla",
#                label="cool",
#                released="2018")
# session.add(album1)
# session.commit()
#
# song1 = Song(album=album1,
#              title="Song 1",
#              position="1")
# session.add(song1)
# session.commit()
#
# # test
# print session.query(Genre).one().name
# print session.query(Album).one().title
# print session.query(Song).one().title

# use discogs API to get my current collection

# Discogs API Token to be included in the GET request headers
HEADER = {'Authorization': 'Discogs token=XdxDFyuAEfqZtiIMPBAMPOtXsqpCpqlnHUKDCdui'}


def getReleasesID(username):
    """Look up all the folders in the user collection
    Args: username
    Return: list of releases ids
    """
    url = "https://api.discogs.com/users/{}/collection/folders".format(username)
    h = httplib2.Http()

    # query to get all folders in the collection
    folders = json.loads(h.request(
        url,
        'GET',
        headers=HEADER)[1])['folders']
    folders_id = []
    for folder in folders:
        if folder['id'] != 0:
            folders_id.append(folder['id'])

    # Loop over folder ids to get all releases in the collection:
    releases_id = []
    for id in folders_id:
        url = "https://api.discogs.com/users/{}/collection/folders/{}/releases".format(username, id)
        releases = json.loads(h.request(
            url,
            'GET',
            headers=HEADER)[1])['releases']
        for release in releases:
            releases_id.append(release['id'])
    return releases_id


def getReleaseInfo(id_str):
    """Get release infos
    Args: release id string
    Return: dictionary
    """
    url = 'https://api.discogs.com/releases/{}'.format(id_str)
    infos = json.loads(httplib2.Http().request(url, headers=HEADER)[1])
    # artist
    try:
        artist = infos['artists'][0]['name']
    except KeyError:
        artist = ''
    try:
        title = infos['title']
    except KeyError:
        title = ''
    try:
        released = infos['released']
    except KeyError:
        released = ''
    genre = infos['genres'][0]
    label = infos['labels'][0]['name']
    songs = [{
            'position': track['position'],
            'title': track['title']
            } for track in infos['tracklist']
            ]
    return {
            'genre': genre,
            'artist': artist,
            'title': title,
            'label': label,
            'released': released,
            'songs': songs
            }


def populateDb(username):
    """Add items found in the user's Discogs collection to the sqlite DB
    """
    for release in getReleasesID(username):
        infos = getReleaseInfo(release)

        if not session.query(Genre).filter_by(name=infos['genre']).first():
            genre = Genre(name=infos['genre'])
            session.add(genre)
            session.commit()
        else:
            genre = session.query(Genre).filter_by(name=infos['genre']).first()
        album = Album(
                title=infos['title'],
                artist=infos['artist'],
                label=infos['label'],
                released=infos['released'],
                genre=genre
                )
        session.add(album)
        session.commit()

        for song in infos['songs']:
            song = Song(
                        position=song['position'],
                        title=song['title'],
                        album=album
                        )
            session.add(song)
            session.commit()
    print 'DB populated with Discogs data!'
    #test
    print len(session.query(Album).all())


populateDb('Gry0u')

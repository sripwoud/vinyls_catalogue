from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker, scoped_session
from database_setup import Base, Genre, Album, Song, engine
import httplib2
import json
import pprint

pp = pprint.PrettyPrinter(indent=4)

Base.metadata.bind = engine
DBSession = scoped_session(sessionmaker(bind=engine))
session = DBSession()


def getReleasesID(username, token):
    """Look up all the folders in the user collection
    Args: username, token
    Return: list of releases ids
    """
    url = "https://api.discogs.com/users/{}/collection/folders".format(username)
    h = httplib2.Http()
    header = {'Authorization': 'Discogs token={}'.format(token)}

    # query to get all folders in the collection
    folders = json.loads(h.request(
        url,
        'GET',
        headers=header)[1])['folders']
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
            headers=header)[1])['releases']
        for release in releases:
            releases_id.append(release['id'])
    return releases_id


def getReleaseInfo(id_str, token):
    """Get release infos
    Args: release id string
    Return: dictionary
    """
    url = 'https://api.discogs.com/releases/{}'.format(id_str)
    header = {'Authorization': 'Discogs token={}'.format(token)}
    infos = json.loads(httplib2.Http().request(url, headers=header)[1])
    # artist
    try:
        artist = infos['artists'][0]['name']
    except KeyError:
        artist = 'Unknown'
    try:
        title = infos['title']
    except KeyError:
        return
    try:
        released = infos['released']
    except KeyError:
        released = 'Unknown'
    try:
        genre = infos['genres'][0]
    except KeyError:
        genre = 'Uncategorized'
    try:
        label = infos['labels'][0]['name']
    except KeyError:
        label = 'Unknown'
    try:
        songs = [{
                'position': track['position'],
                'title': track['title']
                } for track in infos['tracklist']
                ]
    except KeyError:
        return
    try:
        image = infos['images'][0]['uri']
    except KeyError:
        image = '/static/vinyl-record.svg'
    return {
            'genre': genre,
            'artist': artist,
            'title': title,
            'label': label,
            'released': released,
            'songs': songs
            }


def populateDb(username, token):
    """Add items found in the user's Discogs collection to the sqlite DB
    """
    for release in getReleasesID(username, token):
        infos = getReleaseInfo(release, token)
        if infos:
            if not session.query(Genre).filter_by(name=infos['genre']).first():
                genre = Genre(name=infos['genre'])
                session.add(genre)
                session.commit()
                print 'Genre added'
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
            print 'Album added'

            for song in infos['songs']:
                song = Song(
                            position=song['position'],
                            title=song['title'],
                            album=album
                            )
                session.add(song)
                session.commit()
                print 'song added'
    print 'Insertion of new items in DB completed !'
    # test
    print len(session.query(Album).all())


if __name__ == '__main__':
    username = raw_input("Enter your username:")
    token = raw_input("Enter your Discogs API token: ")
    populateDb(username, token)

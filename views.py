from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, scoped_session
from database_setup import Base, Genre, Album, Song, engine
from addcollection import session
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
# engine = create_engine('sqlite:///vinyls.db')
# Base.metadata.bind = engine
# DBSession = sessionmaker(bind=engine)
# session = scoped_session(DBSession())

app = Flask(__name__)


# API Endpoints ---------------------------------
@app.route('/genres/json/')
def genresJSON():
    genres = session.query(Genre).all()
    return jsonify([genre.serialize for genre in genres])


@app.route('/genre/<int:genre_id>/json/')
def releasesJSON(genre_id):
    releases = session.query(Album).filter_by(genre_id=genre_id).all()
    return jsonify([release.serialize for release in releases])


@app.route('/release/<int:release_id>/json/')
def songsJSON(release_id):
    songs = session.query(Song).filter_by(release_id=release_id).all()
    return jsonify([song.serialize for song in songs])
    

@app.route('/')
@app.route('/genres/')
def showGenres():
    genres_count = session.query(Genre.id, Genre.name, func.count(Album.genre_id)).outerjoin(Album).group_by(Genre).order_by(Genre.name).all()
    return render_template('genres.html', genres_count=genres_count)


# -------------------------------------------------- GENRE
@app.route('/genre/new/', methods=['GET', 'POST'])
def newGenre():
    if request.method == 'POST':
        if not session.query(Genre).filter_by(name=request.form['name']).first():
            session.add(Genre(name=request.form['name']))
            session.commit()
            flash('New Genre added!')
            return redirect(url_for('showGenres'))
        else:
            flash('This genre already exists!')
            return render_template('newgenre.html')
    if request.method == 'GET':
        return render_template('newgenre.html')


@app.route('/genre/<int:genre_id>/edit/', methods=['GET', 'POST'])
def editGenre(genre_id):
    genre = session.query(Genre).filter_by(id=genre_id).one()
    if request.method == 'POST':
        if request.form['name']:
            genre.name = request.form['name']
            session.add(genre)
            session.commit()
            flash('Genre updated!')
        return redirect(url_for('showGenres'))
    return render_template('editgenre.html', genre=genre)


@app.route('/genre/<int:genre_id>/delete/', methods=['GET', 'POST'])
def deleteGenre(genre_id):
    genre = session.query(Genre).filter_by(id=genre_id).one()
    if request.method == 'POST':
        session.delete(genre)
        session.commit()
        flash('Genre deleted!')
        return redirect(url_for('showGenres'))
    else:
        return render_template('deletegenre.html', genre=genre)


# -------------------------------------------------- RELEASES
@app.route('/genre/<int:genre_id>/')
def showReleases(genre_id):
    genre = session.query(Genre).filter_by(id=genre_id).one()
    releases = session.query(Album).filter_by(genre_id=genre_id).order_by(Album.title).all()
    return render_template('releases.html', genre=genre, releases=releases)


@app.route('/genre/<int:genre_id>/new/', methods=['GET', 'POST'])
def newRelease(genre_id):
    genre = session.query(Genre).filter_by(id=genre_id).one()
    if request.method == 'POST':
        release = Album(title=request.form['title'],
                        artist=request.form['artist'],
                        label=request.form['label'],
                        released=request.form['released'],
                        genre_id=genre.id)
        session.add(release)
        session.commit()
        flash('New release added!')
        return redirect(url_for('showReleases', genre_id=genre_id))
    if request.method == 'GET':
        return render_template('newrelease.html', genre=genre)


@app.route('/genre/<int:genre_id>/<int:release_id>/edit/',
           methods=['GET', 'POST'])
def editRelease(genre_id, release_id):
    genre = session.query(Genre).filter_by(id=genre_id).one()
    release = session.query(Album).filter_by(id=release_id).one()
    if request.method == 'POST':
        if request.form['title']:
            release.title = request.form['title']
        if request.form['artist']:
            release.artist = request.form['artist']
        if request.form['label']:
            release.label = request.form['label']
        if request.form['released']:
            release.released = request.form['released']
        session.add(release)
        session.commit()
        flash('Release updated!')
        return redirect(url_for('showReleases', genre_id=genre_id))
    return render_template('editrelease.html', genre=genre, release=release)


@app.route('/genre/<int:genre_id>/<int:release_id>/delete/', methods=['GET', 'POST'])
def deleteRelease(genre_id, release_id):
    genre = session.query(Genre).filter_by(id=genre_id).one()
    release = session.query(Album).filter_by(id=release_id).one()
    if request.method == 'POST':
        session.delete(release)
        session.commit()
        flash('Release deleted!')
        return redirect(url_for('showReleases', genre_id=genre_id))
    if request.method == 'GET':
        return render_template('deleterelease.html', genre=genre, release=release)


# -------------------------------------------------- SONGS
@app.route('/release/<int:release_id>/')
def showSongs(release_id):
    release = session.query(Album).filter_by(id=release_id).one()
    songs = session.query(Song).filter_by(release_id=release_id).order_by(Song.position).all()
    return render_template('songs.html', release=release, songs=songs)


@app.route('/release/<int:release_id>/new/', methods=['GET', 'POST'])
def newSong(release_id):
    release = session.query(Album).filter_by(id=release_id).one()
    if request.method == 'POST':
        song = Song(title=request.form['title'],
                     position=request.form['position'],
                     release_id=release.id)
        session.add(song)
        session.commit()
        flash('New song added!')
        return redirect(url_for('showSongs', release_id=release_id))
    if request.method == 'GET':
        return render_template('newsong.html', release=release)


@app.route('/release/<int:release_id>/<int:song_id>/edit/',
           methods=['GET', 'POST'])
def editSong(song_id, release_id):
    song = session.query(Song).filter_by(id=song_id).one()
    release = session.query(Album).filter_by(id=release_id).one()
    if request.method == 'POST':
        if request.form['title']:
            song.title = request.form['title']
        if request.form['position']:
            song.position = request.form['position']
        session.add(song)
        session.commit()
        flash('Song updated!')
        return redirect(url_for('showSongs', release_id=release_id))
    return render_template('editsong.html', song=song, release=release)


@app.route('/release/<int:release_id>/<int:song_id>/delete/', methods=['GET', 'POST'])
def deleteSong(song_id, release_id):
    song = session.query(Song).filter_by(id=song_id).one()
    release = session.query(Album).filter_by(id=release_id).one()
    if request.method == 'POST':
        session.delete(song)
        session.commit()
        flash('Song deleted!')
        return redirect(url_for('showSongs', release_id=release_id))
    if request.method == 'GET':
        return render_template('deletesong.html', song=song, release=release)
# TODO: Make API endpoints

# TODO: Add OAuth


if __name__ == '__main__':
    app.secret_key = 'pass'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Genre, Album, Song
from flask import Flask, render_template, redirect, url_for, request, flash
engine = create_engine('sqlite:///vinyls.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

app = Flask(__name__)


@app.route('/')
@app.route('/genres/')
def showGenres():
    genres_count = session.query(Genre.id, Genre.name, func.count(Album.genre_id)).outerjoin(Album).group_by(Genre).order_by(Genre.name).all()
    return render_template('genres.html', genres_count=genres_count)


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
            falsh('Genre updated!')
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
    return 'Page to edit release {} of genre {}'.format(release_id, genre_id)


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


# TODO: Make API endpoints

# TODO: Add OAuth


if __name__ == '__main__':
    app.secret_key = 'pass'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)

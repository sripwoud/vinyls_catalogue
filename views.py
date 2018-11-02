from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Genre, Album, Song
from flask import Flask
engine = create_engine('sqlite:///vinyls.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

app = Flask(__name__)

# TODO: MAKE ROUTES
@app.route('/')
@app.route('/genres/')
def showGenres():
    return 'Page to display all genres'


@app.route('/genre/new/', methods=['GET', 'POST'])
def newGenre():
    return 'Page to add new genre'


@app.route('/genre/<int:genre_id>/edit/', methods=['GET', 'POST'])
def editGenre(genre_id):
    return 'Page to edit existing genre {}'.format(genre_id)


@app.route('/genre/<int:genre_id>/delete/')
def deleteGenre(genre_id):
    return 'Page to delete existing genre'


@app.route('/genre/<int:genre_id>/')
def showReleases(genre_id):
    return 'Page to display all releases of genre {}'.format(genre_id)


@app.route('/genre/<int:genre_id>/new/', methods=['GET', 'POST'])
def newRelease(genre_id):
    return 'Page to add new release to genre {}'.format(genre_id)


@app.route('/genre/<int:genre_id>/<int:release_id>/edit/', methods=['GET', 'POST'])
def editRelease(genre_id, release_id):
    return 'Page to edit release {} of genre {}'.format(release_id, genre_id)


@app.route('/genre/<int:genre_id>/<int:release_id>/delete/')
def deleteRelease(genre_id, release_id):
    return 'Page to delete release {} of genre {}'.format(release_id, genre_id)


# TODO: Make API endpoints

# TODO: Add OAuth


if __name__ == '__main__':
    app.secret_key = 'pass'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)

from database_setup import Genre, Album, Song
from addcollection import session
from flask import (Flask, render_template, redirect, url_for, request,
                   flash, jsonify, make_response)
from flask import session as login_session
import httplib2
import json
from oauth2client.client import flow_from_clientsecrets, AccessTokenCredentials
from oauth2client.client import FlowExchangeError
import random
import requests
from sqlalchemy import func
import string

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

app = Flask(__name__)

# Anti Foregery token and login------------------------


@app.route('/login/')
def showLogin():
    # generate random token
    state = ''.join(
        random.choice(
            string.ascii_uppercase + string.digits) for x in range(32))
    # Store token for later validation
    login_session['state'] = state
    return render_template('login.html', state=state)


# Google Sign In Routes -------------------------

@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Anti forgery token check
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # collect one-time code
    code = request.data
    try:
        # exchange it for credentials:
        # create oauth_flow object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        # initiate exhange of one time code for credentials
        credentials = oauth_flow.step2_exchange(code)
        # return credentials
    # handle Error
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check if acess token in credentials object is valid
    access_token = credentials.access_token
    url = 'https://www.googleapis.com/oauth2/v1/' +
          'tokeninfo?access_token={}'.format(access_token)
    result = json.loads(httplib2.Http().request(url, 'GET')[1])
    # if error in access token, abort
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
    # check that access token is for intended user
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID"), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # check that access token is for intended app
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID doesn't match app's"), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # check if user already logged in
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'

    # Store access token for later use
    login_session['gplus_id'] = gplus_id
    login_session['access_token'] = access_token

    # Get user info from google account
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = json.loads(answer.text)
    # store user data for later use
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = """
    <h1>
        Welcome, {}
    </h1>
    <img src='{}'
         style='width: 300px;
         height: 300px;
         border-radius: 150px;
         -webkit-border-radius: 150px;
         -moz-border-radius:150px' >
    """.format(login_session['username'],
               login_session['picture'])
    flash("You are now logged in as {}".format(login_session['username']))
    return output


# revoke access token and reset login_session
@app.route('/gdisconnect/')
def gdisconnect():
    # Only disconnect a connected user
    access_token = login_session['access_token']
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # revoke current user
    url = 'https://accounts.google.com/o/oauth2/' +
          'revoke?token={}'.format(access_token)
    result = httplib2.Http().request(url, 'GET')[0]
    # if request successful reset session
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['email']
        del login_session['gplus_id']
        del login_session['picture']
        del login_session['username']

        flash('Successfully disconnected.')
        return redirect(url_for('showGenres'))
    # Otherwise display error message
    else:
        response = make_response(
            json.dumps('Failed to revoke token for the given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


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
    # check if user logged in:
    user = login_session['username']
    genres_count = (session
                    .query(Genre.id, Genre.name, func.count(Album.genre_id))
                    .outerjoin(Album)
                    .group_by(Genre)
                    .order_by(Genre.name)
                    .all())
    return render_template('genres.html', genres_count=genres_count, user=user)


# -------------------------------------------------- GENRES ROUTES
@app.route('/genre/new/', methods=['GET', 'POST'])
def newGenre():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        if not (session
                .query(Genre).filter_by(name=request.form['name']).first()):
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
    if 'username' not in login_session:
        return redirect('/login')
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
    if 'username' not in login_session:
        return redirect('/login')
    genre = session.query(Genre).filter_by(id=genre_id).one()
    if request.method == 'POST':
        session.delete(genre)
        session.commit()
        flash('Genre deleted!')
        return redirect(url_for('showGenres'))
    else:
        return render_template('deletegenre.html', genre=genre)


# -------------------------------------------------- RELEASES ROUTES
@app.route('/genre/<int:genre_id>/')
def showReleases(genre_id):
    genre = session.query(Genre).filter_by(id=genre_id).one()
    releases = (session
                .query(Album)
                .filter_by(genre_id=genre_id).order_by(Album.title).all())
    return render_template('releases.html', genre=genre, releases=releases)


@app.route('/genre/<int:genre_id>/new/', methods=['GET', 'POST'])
def newRelease(genre_id):
    if 'username' not in login_session:
        return redirect('/login')
    genre = session.query(Genre).filter_by(id=genre_id).one()
    if request.method == 'POST':
        release = Album(title=request.form['title'],
                        artist=request.form['artist'],
                        label=request.form['label'],
                        released=request.form['released'],
                        image=request.form['image'],
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
    if 'username' not in login_session:
        return redirect('/login')
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
        if request.form['image']:
            release.image = request.form['image']
        session.add(release)
        session.commit()
        flash('Release updated!')
        return redirect(url_for('showReleases', genre_id=genre_id))
    return render_template('editrelease.html', genre=genre, release=release)


@app.route('/genre/<int:genre_id>/<int:release_id>/delete/',
           methods=['GET', 'POST'])
def deleteRelease(genre_id, release_id):
    if 'username' not in login_session:
        return redirect('/login')
    genre = session.query(Genre).filter_by(id=genre_id).one()
    release = session.query(Album).filter_by(id=release_id).one()
    if request.method == 'POST':
        session.delete(release)
        session.commit()
        flash('Release deleted!')
        return redirect(url_for('showReleases', genre_id=genre_id))
    if request.method == 'GET':
        return render_template('deleterelease.html',
                               genre=genre, release=release)


# -------------------------------------------------- SONGS ROUTES
@app.route('/release/<int:release_id>/')
def showSongs(release_id):
    release = session.query(Album).filter_by(id=release_id).one()
    songs = (session
             .query(Song)
             .filter_by(release_id=release_id).order_by(Song.position).all())
    return render_template('songs.html', release=release, songs=songs)


@app.route('/release/<int:release_id>/new/', methods=['GET', 'POST'])
def newSong(release_id):
    if 'username' not in login_session:
        return redirect('/login')
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
    if 'username' not in login_session:
        return redirect('/login')
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


@app.route('/release/<int:release_id>/<int:song_id>/delete/',
           methods=['GET', 'POST'])
def deleteSong(song_id, release_id):
    if 'username' not in login_session:
        return redirect('/login')
    song = session.query(Song).filter_by(id=song_id).one()
    release = session.query(Album).filter_by(id=release_id).one()
    if request.method == 'POST':
        session.delete(song)
        session.commit()
        flash('Song deleted!')
        return redirect(url_for('showSongs', release_id=release_id))
    if request.method == 'GET':
        return render_template('deletesong.html', song=song, release=release)


if __name__ == '__main__':
    app.secret_key = 'pass'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
    print 'Application runnning...go to http://localhost:5000'

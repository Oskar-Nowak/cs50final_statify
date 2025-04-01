import requests, os
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from urllib import parse
from datetime import datetime
from json import dumps

from spotify_api import get_auth_header, token_required, time_range_required, set_displayed_time_range

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

load_dotenv()
SPOTIFY_CLIENT_ID = os.getenv("CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("REDIRECT_URI")

SPOTIFY_AUTH_URL = 'https://accounts.spotify.com/authorize'
SPOTIFY_TOKEN_URL = 'https://accounts.spotify.com/api/token'
SPOTIFY_API_BASE_URL = 'https://api.spotify.com/v1'


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache , no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=['GET', 'POST'])
def index():

    # Access token check
    if 'access_token' not in session:
            return render_template("login.html")
        
    # Token expiration check
    if datetime.now().timestamp() > session['expires_at']:
        return redirect("/refresh-token")
    
    headers = get_auth_header(session['access_token'])

    # Make an API call to recive the currently logged in profile info.
    if 'user_id' not in session:
        response = requests.get(SPOTIFY_API_BASE_URL + '/me', headers=headers)
        if not (response):
            return jsonify({'Error': 'Empty dictionary'})
        
        account_info = response.json()
        session['user_id'] = account_info['id']

    return render_template("homepage.html")


@app.route("/login")
def login():
    # Define the scopes that the user will need to access the necessary data.
    scope = "user-read-private user-read-email user-top-read playlist-modify-public playlist-modify-private"
    params = {
        'client_id': SPOTIFY_CLIENT_ID,
        'redirect_uri': SPOTIFY_REDIRECT_URI,
        'response_type': 'code',
        'scope': scope,
        'show_dialog': True
    }
    auth_url = f"{SPOTIFY_AUTH_URL}?{parse.urlencode(params)}"

    return redirect(auth_url)

@app.route("/logout" )
def logout():
    # Since access token is stored in session, we just clear the session.
    session.clear()
    return redirect("/")


# This is the route provided on the Spotify Dashboard as the callback route, where the access token is sent after successful authorization.
@app.route("/callback")
def callback():
    if 'error' in request.args:
        return jsonify({"Error": request.args['error']})

    if 'code' in request.args:
        req_body = {
            'code': request.args['code'],
            'grant_type': 'authorization_code',
            'redirect_uri': SPOTIFY_REDIRECT_URI,
            'client_id': SPOTIFY_CLIENT_ID,
            'client_secret': SPOTIFY_CLIENT_SECRET,
        }
    response = requests.post(SPOTIFY_TOKEN_URL, data=req_body)
    token_info = response.json()

    # We store the access token itself with all of the neccessary data in session.
    session['access_token']  = token_info['access_token']
    session['refresh_token'] = token_info['refresh_token']
    session['expires_at']    = datetime.now().timestamp() + token_info['expires_in']

    return redirect("/")


@app.route("/refresh-token")
def refresh_token():
    if 'refresh_token' not in session:
        return redirect("/login")
    
    if datetime.now().timestamp() > session['expires_at']:
        request_body = {
            'grant_type': 'refresh_token',
            'refresh_token': session['refresh_token'],
            'client_id': SPOTIFY_CLIENT_ID,
            'client_secret': SPOTIFY_CLIENT_SECRET,
        }
        response = requests.post(SPOTIFY_TOKEN_URL, data=request_body)
        new_token_info = response.json()

        session['access_token'] = new_token_info['access_token']
        session['expires_at']   = datetime.now().timestamp() + new_token_info['expires_in']

    return redirect("/")


@app.route("/favourite-tracks", methods=['GET', 'POST'])
@token_required
@time_range_required
def favourite_tracks():
        headers = get_auth_header(session['access_token'])
        response = requests.get(SPOTIFY_API_BASE_URL + '/me/top/tracks?time_range=' + session['time_range'] + '&limit=20', headers=headers)
        
        if not (response):
            return jsonify({'Error': 'Empty dictionary'})
        
        top20_listened_to_tracks = response.json()
        track_data = [
        {
            'track_name': track['name'],
            'track_url': track['external_urls']['spotify'],
            'track_uri': track['uri'],
            'artist_name': [artist['name'] for artist in track['artists']],
            'album_cover_url': track['album']['images'][0]['url'],
        }
        for track in top20_listened_to_tracks['items']
    ]
    
    # Saving the uris in session so they can be easily accessed while creating playlists.
        session['track_uris'] = [track['track_uri'] for track in track_data]

        return render_template("favourite-tracks.html", track_data=track_data, displayed_time_range=set_displayed_time_range())


@app.route("/favourite-artists", methods=['GET', 'POST'])
@token_required
@time_range_required
def favourite_artists():
        headers = get_auth_header(session['access_token'])
        response = requests.get(SPOTIFY_API_BASE_URL + '/me/top/artists?time_range=' + session['time_range'] + '&limit=20', headers=headers)
        
        if not (response):
            return jsonify({'Error': 'Empty dictionary'})
        
        top20_listened_to_artists = response.json()

        artist_data = [
            {
                'artist_name': artist['name'],
                'artist_url': artist['external_urls']['spotify'],
                'genres': artist['genres'],
                'artist_profile_photo': artist['images'][1]['url'],
            }
            for artist in top20_listened_to_artists['items']
        ]
        # return jsonify(artist_data)

        return render_template("favourite-artists.html", artist_data=artist_data, displayed_time_range=set_displayed_time_range())


@app.route("/favourite-genres", methods=['GET', 'POST'])
@token_required
@time_range_required
def favourite_genres():
    headers = get_auth_header(session['access_token'])
    response = requests.get(SPOTIFY_API_BASE_URL + '/me/top/artists?time_range=' + session['time_range'] + '&limit=20', headers=headers)

    if not (response):
        return jsonify({'Error': 'Empty dictionary'})
    
    top20_listened_to_genres = response.json()

    genres_data = {}
    for item in top20_listened_to_genres['items']:
        for genre in item['genres']:
            capitalized_genre = genre.capitalize()
            size = len(genres_data)
            if capitalized_genre not in genres_data and size < 20:
                genres_data[capitalized_genre] = 1
            elif capitalized_genre in genres_data:
                genres_data[capitalized_genre] += 1
            else:
                continue

    # Sort the dictionary so by the number value, so that the highest rated genre will appear first.
    sorted_genres_data = sorted(genres_data.items(), key=lambda item : item[1], reverse=True)
    print(sorted_genres_data)
    # Converts the Python Object, an array of tuples in this case into a JSON string.
    sorted_genres_json = dumps(sorted_genres_data)

    return render_template("favourite-genres.html", sorted_genres_data=sorted_genres_json, displayed_time_range=set_displayed_time_range())
        

@app.route("/create-playlist", methods=['GET', 'POST'])
@token_required
def create_playlist():
    if request.method == 'POST':
        headers = {
            'Authorization': 'Bearer ' + session['access_token'],
            'Content-Type': 'application/json',
        }

        current_date_and_time = datetime.now().replace(second=0, microsecond=0).strftime("%Y-%m-%d %H:%M")
        create_playlist_request_body = {
            'name': 'Top20 ' + current_date_and_time,
            'description': 'Top 20 songs from ' + set_displayed_time_range() + '. ' + 'Created by Statify.',
            'public': False,
        }
        create_playlist_query = '/users' + '/' + session['user_id'] + '/playlists'
    
        # By chaning the name of a request body argument to 'json', we ensure that the data will be sent in JSON format.
        response = requests.post(SPOTIFY_API_BASE_URL + create_playlist_query, headers=headers, json=create_playlist_request_body)
        if not (response):
            return jsonify({'Error': 'Empty dictionary'})

        playlist_data = response.json()
        playlist_url = playlist_data['external_urls']['spotify']
        playlist_id = playlist_data['id']

        add_items_to_playlist_request_body = {
            'uris': session['track_uris'],
            'position': 0,
        }
        add_items_to_playlist_query = '/playlists' + '/' + playlist_id + '/tracks'
        response = requests.post(SPOTIFY_API_BASE_URL + add_items_to_playlist_query, headers=headers, json=add_items_to_playlist_request_body)

        flash('Playlist created successfully!\nLink: ' + playlist_url)
        return jsonify({"message": "Playlist created successfully!", "playlist_url": playlist_url}), 200
        
    else:
        return redirect("/")
    
 
if __name__ == '__main__':
    app.run(debug=True)
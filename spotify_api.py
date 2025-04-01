import os
from dotenv import load_dotenv
from functools import wraps
from flask import redirect, request, session, jsonify
from datetime import datetime

load_dotenv()   
SPOTIFY_CLIENT_ID = os.getenv("CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("CLIENT_SECRET")
SPOTIFY_REDIRECT_URL = os.getenv("REDIRECT_URL")


def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Access token check
        if 'access_token' not in session:
            return redirect("/login")
        
        # Token expiration check
        if datetime.now().timestamp() > session['expires_at']:
            return redirect("/refresh-token")
        
        # If everything is fine, proceed to the original function
        return f(*args, **kwargs)
    return decorated_function


def time_range_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get the time range from a form, base is short_term
        session['time_range'] = request.form.get('time_range', 'short_term')
        if 'time_range' not in session:
            return jsonify({'Error': 'Time range is required.'}), 400
        
        # If everything is fine, proceed to the original function
        return f(*args, **kwargs)
    return decorated_function


def set_displayed_time_range():
    if session['time_range'] == 'short_term':
        displayed_time_range = 'last month'
    elif session['time_range'] == 'medium_term':
        displayed_time_range = 'last 6 months'
    elif session['time_range']== 'long_term':
        displayed_time_range = 'last 12 months'

    return displayed_time_range

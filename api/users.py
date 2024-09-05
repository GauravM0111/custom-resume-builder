from flask import Blueprint, request, redirect, session, url_for
from google_auth_oauthlib.flow import Flow
from services.UserService import UserService
import os

users_bp = Blueprint('users', __name__, url_prefix='/users')

GOOGLE_OAUTH_CONFIG = {
    "web": {
        "client_id": os.getenv('GOOGLE_OAUTH_CLIENT_ID'),
        "client_secret": os.getenv('GOOGLE_OAUTH_CLIENT_SECRET'),
        "redirect_uris": [
            url_for('users.google_oauth2_callback', _external=True)
        ],
        "auth_uri": os.getenv('GOOGLE_OAUTH_AUTH_URI'),
        "token_uri": os.getenv('GOOGLE_OAUTH_TOKEN_URI')
    }
}


@users_bp.route('/', methods=['GET'])
def create_user():
    flow = Flow.from_client_config(
        client_config=GOOGLE_OAUTH_CONFIG,
        scopes=['https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile'],
        redirect_uri=url_for('users.google_oauth2_callback', _external=True)
    )

    authorization_url, session["state"] = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )

    return redirect(authorization_url), 302


@users_bp.route('/googleoauth2callback', methods=['GET'])
def google_oauth2_callback():
    if 'state' not in session:
        return 'State not found', 400

    if request.args.get('state') != session['state']:
        return 'Invalid state', 400

    if 'error' in request.args:
        return request.args['error'], 400
    
    if 'code' not in request.args:
        return 'Code not found', 400
    
    flow = Flow.from_client_config(
        client_config=GOOGLE_OAUTH_CONFIG,
        scopes=['https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile'],
        redirect_uri=url_for('users.google_oauth2_callback', _external=True),
        state=session["state"]
    )

    flow.fetch_token(code=request.args['code'])

    # use credentials to get user info from google apis
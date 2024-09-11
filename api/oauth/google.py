import hashlib
from flask import Blueprint, request, redirect, session, url_for, make_response
import os
import requests
from urllib.parse import urlencode
import ast
from clients.redis_client import RedisClient
from settings.settings import GOOGLE_OAUTH_CLIENT_ID, GOOGLE_OAUTH_CLIENT_SECRET

google_oauth_bp = Blueprint('googleoauth', __name__, url_prefix='/googleoauth')


def get_user():
    state = hashlib.sha256(os.urandom(1024)).hexdigest()
    session['state'] = state

    params = {
        'client_id': GOOGLE_OAUTH_CLIENT_ID,
        'response_type': 'code',
        'scope': 'openid email profile',
        'redirect_uri': url_for('googleoauth.oauth2_callback', _external=True),
        'state': state,
        'nonce': hashlib.sha256(os.urandom(1024)).hexdigest()
    }

    response = requests.get('{}?{}'.format(retrieve_discovery_document()['authorization_endpoint'], urlencode(params)))

    if not response.ok:
        return make_response(response.json(), response.status_code)

    return {}, 204


@google_oauth_bp.route('/callback', methods=['GET'])
def oauth2_callback():
    if 'state' not in session:
        return 'State not found', 400

    if request.args.get('state', '') != session['state']:
        return 'Invalid state', 400

    if 'error' in request.args:
        return request.args['error'], 400
    
    if 'code' not in request.args:
        return 'Code not found', 400
    
    discovery_document = retrieve_discovery_document()
    
    response = requests.post(
        url=discovery_document['token_endpoint'],
        params={
            'code': request.args['code'],
            'client_id': GOOGLE_OAUTH_CLIENT_ID,
            'client_secret': GOOGLE_OAUTH_CLIENT_SECRET,
            'redirect_uri': url_for('googleoauth.oauth2_callback', _external=True),
            'grant_type': 'authorization_code'
        }
    )

    if not response.ok:
        return make_response(response.json(), response.status_code)
    
    credentials = response.json()
    
    response = requests.get(
        url=discovery_document['userinfo_endpoint'],
        headers={
            'Authorization': f"Bearer {credentials['access_token']}"
        }
    )

    return make_response(response.json(), 200)


def retrieve_discovery_document(ignore_cache: bool = False) -> dict:
    SECONDS_IN_A_DAY = 24 * 60 * 60
    DISCOVERY_DOCUMENT_URL = 'https://accounts.google.com/.well-known/openid-configuration'

    discovery_document: dict = None

    if not ignore_cache:
        discovery_document = RedisClient().get_data('google_oauth_discovery_document')

    if not discovery_document:
        discovery_document = requests.get(DISCOVERY_DOCUMENT_URL).json()
        RedisClient().set_data(
            'google_oauth_discovery_document',
            str(discovery_document),
            expires_in_seconds=SECONDS_IN_A_DAY
        )
    else:
        discovery_document = ast.literal_eval(discovery_document)
    
    return discovery_document

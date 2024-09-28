from urllib.parse import urlencode
from fastapi import APIRouter, Cookie
from fastapi.responses import RedirectResponse
from typing import Annotated
from models.users import UserCreate
from services.user_service import create_or_get_user
from db.core import get_db
from sqlalchemy.orm import Session
from fastapi.params import Depends
from services.session_service import get_sessionid_cookie_config
import hashlib
import os
import requests
from settings.settings import (
    BASE_URL,
    GOOGLE_DISCOVERY_DOCUMENT_URL,
    GOOGLE_OAUTH_CLIENT_ID,
    GOOGLE_OAUTH_CLIENT_SECRET
)

router = APIRouter(prefix='/googleoauth')


@router.get('/')
async def sign_in():
    state = hashlib.sha256(os.urandom(1024)).hexdigest()

    params = {
        'client_id': GOOGLE_OAUTH_CLIENT_ID,
        'response_type': 'code',
        'scope': 'openid email profile',
        'redirect_uri': BASE_URL + router.url_path_for('callback'),
        'state': state,
        'nonce': hashlib.sha256(os.urandom(1024)).hexdigest()
    }

    response = RedirectResponse(url='{}?{}'.format(retrieve_discovery_document()['authorization_endpoint'], urlencode(params)))
    response.set_cookie(
        key='google_oauth_state',
        value=state,
        httponly=True,
        secure=False,   # set to True in prod
        samesite='lax',
        domain=None,    # set to actual domain in prod
        max_age=60 * 5  # 5 minutes
    )
    return response


@router.get('/callback')
async def callback(state: str, code: str, error: str = None, google_oauth_state: Annotated[str | None, Cookie()] = None, db: Session = Depends(get_db)):
    if not google_oauth_state:
        return {'error': 'State not found'}, 400

    if state != google_oauth_state:
        return 'Invalid state', 400

    if error:
        return {'error': error}, 400
    
    google_discovery_document = retrieve_discovery_document()

    response = requests.post(
        url=google_discovery_document['token_endpoint'],
        params={
            'code': code,
            'client_id': GOOGLE_OAUTH_CLIENT_ID,
            'client_secret': GOOGLE_OAUTH_CLIENT_SECRET,
            'redirect_uri': BASE_URL + router.url_path_for('callback'),
            'grant_type': 'authorization_code'
        }
    )

    if not response.ok:
        return response.json(), response.status_code
    
    response = requests.get(
        url=google_discovery_document['userinfo_endpoint'],
        headers={
            'Authorization': f"Bearer {response.json()['access_token']}"
        }
    )

    if not response.ok:
        return response.json(), response.status_code
    
    try:
        _, session_id = create_or_get_user(UserCreate(**response.json()), db)
    except Exception:
        return {'error': 'failed to create or retrieve user'}
    
    response = RedirectResponse(url='/index')
    response.set_cookie(**get_sessionid_cookie_config(session_id))

    return response


def retrieve_discovery_document() -> dict:
    return requests.get(GOOGLE_DISCOVERY_DOCUMENT_URL).json()
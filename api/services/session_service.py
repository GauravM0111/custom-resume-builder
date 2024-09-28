from typing import Annotated
from fastapi.exceptions import HTTPException
from fastapi import Cookie, Request
from fastapi.params import Depends
from fastapi.responses import Response, RedirectResponse
from redis import Redis
from os import getenv
import uuid
from functools import wraps
from settings.settings import BASE_URL

from models.users import User

from datetime import datetime

NINETY_DAYS_IN_SECONDS = 60 * 60 * 24 * 90


class SessionService():
    def __init__(self) -> None:
        self.redis = Redis(
            host='redis',   # This is the name of the service in the docker-compose file
            port=getenv('REDIS_PORT'),
            decode_responses=True,
            protocol=3
        )


    def create_session(self, user: User) -> str:
        session_id = str(uuid.uuid4())

        # make sure there is no duplicate session_id
        while self.redis.get(f'sessions:{session_id}'):
            session_id = str(uuid.uuid4())

        if not self.redis.set(f'sessions:{session_id}', dict(user), ex=NINETY_DAYS_IN_SECONDS):
            raise Exception(f'session creation failed')

        return session_id


    def get_user_data(self, session_id: str) -> dict:
        return self.redis.get(f'sessions:{session_id}')


def login_required(f):
    @wraps(f)
    def decorated_function(request: Request, *args, **kwargs):
        identity_jwt = request.cookies.get('identity_jwt')
        refresh_token = request.cookies.get('refresh_token')

        if identity_jwt and identity_jwt == 'valid':    # TODO: actual validation
            return f(*args, **kwargs)
        
        if refresh_token:
            user_data = SessionService().get_user_data(refresh_token)
            if user_data:
                identity_jwt = 'valid'  #TODO generate from user_data
                response: Response = f(*args, **kwargs)
                response.set_cookie(**get_identity_jwt_cookie_config(identity_jwt))
                return response
        
        return RedirectResponse(f"{BASE_URL}/signin")
    return decorated_function


def get_current_user(identity_jwt: Annotated[str | None, Cookie()] = None) -> User:
    if not identity_jwt:
        raise HTTPException(status_code=400, detail="user is not logged in")
    
    user_data = {
        'id': 'test_id',
        'email': 'test_email',
        'created_at': datetime.now()
    }    # assign to decoded jwt values
    return User(**user_data)

UserDependency = Annotated[User, Depends(get_current_user)]


def get_sessionid_cookie_config(session_id: str) -> dict:
    return {
        'key': 'refresh_token',
        'value': session_id,
        'httponly': True,
        'secure': False,   # set to True in prod
        'samesite': 'lax',
        'domain': None,    # set to actual domain in prod
        'max_age': NINETY_DAYS_IN_SECONDS
    }


def get_identity_jwt_cookie_config(jwt: str) -> dict:
    return {
        'key': 'identity_jwt',
        'value': jwt,
        'httponly': True,
        'secure': False,   # set to True in prod
        'samesite': 'lax',
        'domain': None,    # set to actual domain in prod
        'max_age': 60 * 15  # 15 minutes in seconds
    }
from clients.redis_client import RedisClient
import uuid
from functools import wraps
from flask import request, redirect, url_for

NINETY_DAYS_IN_SECONDS = 60 * 60 * 24 * 90


class SessionService():
    def __init__(self):
        self.redis = RedisClient()


    def create_session(self, user_id: str):
        session_id = str(uuid.uuid4())

        # make sure there is no duplicate session_id
        while self.redis.get(f'sessions:{session_id}'):
            session_id = str(uuid.uuid4())

        if not self.redis.set(f'sessions:{session_id}', user_id, ex=NINETY_DAYS_IN_SECONDS):
            raise Exception(f'session creation failed')

        return session_id


    def get_user_id(self, session_id: str):
        return self.redis.get(f'sessions:{session_id}')


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        identity_jwt = request.cookies.get('identity_jwt')
        refresh_token = request.cookies.get('refresh_token')

        if identity_jwt:
            # TODO: decode jwt
            user_id = None
            return f(user_id=user_id, *args, **kwargs)
        elif refresh_token:
            user_id = SessionService().get_user_id(refresh_token)

            # TODO: encode jwt into identity_jwt

            return f(user_id=user_id, *args, **kwargs)

        return redirect(url_for('sign_in'))
    return decorated_function
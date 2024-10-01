from redis import Redis
from os import getenv
import uuid

NINETY_DAYS_IN_SECONDS = 60 * 60 * 24 * 90


class SessionService:
    def __init__(self):
        self.redis = Redis(
            host='redis',   # This is the name of the service in the docker-compose file
            port=getenv('REDIS_PORT'),
            decode_responses=True,
            protocol=3
        )


    def create_session(self, user_id: str) -> str:
        session_id = str(uuid.uuid4())

        # make sure there is no duplicate session_id
        while self.redis.get(f'sessions:{session_id}'):
            session_id = str(uuid.uuid4())
        
        if not self.redis.set(f'sessions:{session_id}', user_id, ex=NINETY_DAYS_IN_SECONDS):
            raise Exception(f'session creation failed')
        
        return session_id


    def get_user_id(self, session_id: str) -> str:
        return self.redis.get(f'sessions:{session_id}')


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

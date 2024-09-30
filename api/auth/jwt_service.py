import jwt
from settings.settings import API_SECRET_KEY
from datetime import datetime, timedelta


def generate_jwt(user_id: str) -> str:
    jwt_data = {
        "user_id": user_id,
        "exp": datetime.now() + timedelta(minutes=15)
    }
    return jwt.encode(jwt_data, API_SECRET_KEY, algorithm="HS256")


def get_user_id_from_jwt(identity_jwt: str) -> str:
    return jwt.decode(identity_jwt, API_SECRET_KEY, algorithms="HS256")["user_id"]


def is_valid_jwt(identity_jwt: str) -> bool:
    try:
        jwt.decode(identity_jwt, API_SECRET_KEY, algorithms="HS256")
    except Exception:
        return False

    return True


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

import jwt
from models.users import User
from settings.settings import API_SECRET_KEY
from datetime import datetime, timedelta


def generate_jwt(user: User) -> str:
    jwt_data = {
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "created_at": user.created_at.isoformat(),
            "picture": user.picture,
            "profile": True if user.profile else False,
            "is_guest": user.is_guest
        },
        "exp": datetime.now() + timedelta(minutes=15)
    }
    return jwt.encode(jwt_data, API_SECRET_KEY, algorithm="HS256")


def get_user_data_from_jwt(identity_jwt: str) -> dict:
    return jwt.decode(identity_jwt, API_SECRET_KEY, algorithms="HS256")["user"]


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

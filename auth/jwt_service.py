from datetime import datetime, timedelta, timezone

import jwt

from models.users import User
from services.user_service import UserService
from settings.settings import API_SECRET_KEY


def generate_jwt(user: User) -> str:
    jwt_data = {
        "user": UserService().user_dict_compact(user),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
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
        "key": "identity_jwt",
        "value": jwt,
        "httponly": True,
        "secure": False,  # set to True in prod
        "samesite": "lax",
        "domain": None,  # set to actual domain in prod
        "max_age": 60 * 15,  # 15 minutes in seconds
    }

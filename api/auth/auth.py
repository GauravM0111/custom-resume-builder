from fastapi import Cookie, Response
from fastapi.params import Depends
from fastapi.responses import RedirectResponse
from functools import wraps
from settings.settings import BASE_URL

from models.cookies import AuthToken
from auth.jwt_service import generate_jwt, get_identity_jwt_cookie_config
from .session_service import SessionService


def user_login_required(func):
    @wraps(func)
    async def wrapper(token: AuthToken, *args, **kwargs):
        if token.identity_jwt and token.identity_jwt == 'valid':
            return await func(token, *args, **kwargs)

        if token.refresh_token:
            user_id = SessionService().get_user_id(token.refresh_token)
            if user_id:
                new_identity_jwt = generate_jwt(user_id)
                token.identity_jwt = new_identity_jwt
                response: Response = await func(token, *args, **kwargs)
                response.set_cookie(**get_identity_jwt_cookie_config(new_identity_jwt))
                return response

        return RedirectResponse(url=f'{BASE_URL}/signin')

    return wrapper

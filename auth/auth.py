from fastapi import Response
from functools import wraps

from fastapi.responses import RedirectResponse

from db.core import get_db
from services.user_service import create_guest_user

from models.cookies import AuthToken
from auth.jwt_service import generate_jwt, get_identity_jwt_cookie_config, is_valid_jwt
from auth.session_service import SessionService, get_sessionid_cookie_config


def user_login_required(func):
    @wraps(func)
    async def wrapper(token: AuthToken, *args, **kwargs):
        if token.identity_jwt and is_valid_jwt(token.identity_jwt):
            return await func(token, *args, **kwargs)

        if token.refresh_token:
            user_id = SessionService().get_user_id(token.refresh_token)
            if user_id:
                new_identity_jwt = generate_jwt(user_id)
                token.identity_jwt = new_identity_jwt
                response: Response = await func(token, *args, **kwargs)
                response.set_cookie(**get_identity_jwt_cookie_config(new_identity_jwt))
                return response
        
        # No jwt or refresh token means its a fresh user
        with next(get_db()) as db:
            user, session_id = create_guest_user(db)
        
        new_identity_jwt = generate_jwt(user.id)
        token.identity_jwt = new_identity_jwt

        response = RedirectResponse(url="/")
        response.set_cookie(**get_identity_jwt_cookie_config(new_identity_jwt))
        response.set_cookie(**get_sessionid_cookie_config(session_id))
        return response

    return wrapper

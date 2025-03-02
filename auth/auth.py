from fastapi import Request, Response

from auth.jwt_service import (
    generate_jwt,
    get_identity_jwt_cookie_config,
    get_user_data_from_jwt,
    is_valid_jwt,
)
from auth.session_service import SessionService, get_sessionid_cookie_config
from db.core import get_db
from db.users import get_user_by_id
from models.users import User


async def user_authentication_middleware(request: Request, call_next):
    identity_jwt = request.cookies.get("identity_jwt")
    refresh_token = request.cookies.get("refresh_token")

    if identity_jwt and is_valid_jwt(identity_jwt):
        request.state.user = get_user_data_from_jwt(identity_jwt)
        return await call_next(request)

    if refresh_token:
        if user_id := SessionService().get_user_id(refresh_token):
            with next(get_db()) as db:
                user = get_user_by_id(user_id, db)
            new_identity_jwt = generate_jwt(user)
            request.state.user = get_user_data_from_jwt(new_identity_jwt)
            response: Response = await call_next(request)
            response.set_cookie(**get_identity_jwt_cookie_config(new_identity_jwt))
            return response

    request.state.user = None
    return await call_next(request)


async def login_user_in_response(response: Response, user: User) -> Response:
    session_id = SessionService().create_session(user.id)
    response.set_cookie(**get_identity_jwt_cookie_config(generate_jwt(user)))
    response.set_cookie(**get_sessionid_cookie_config(session_id))
    return response

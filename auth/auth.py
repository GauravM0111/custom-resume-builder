from fastapi import Request, Response
from fastapi.responses import RedirectResponse

from db.core import get_db
from db.users import get_user_by_id
from services.user_service import create_guest_user

from auth.jwt_service import generate_jwt, get_identity_jwt_cookie_config, get_user_data_from_jwt, is_valid_jwt
from auth.session_service import SessionService, get_sessionid_cookie_config


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
    
    with next(get_db()) as db:
        user, session_id = create_guest_user(db)

    new_identity_jwt = generate_jwt(user)
    request.state.user = get_user_data_from_jwt(new_identity_jwt)

    response = RedirectResponse(url="/")
    response.set_cookie(**get_identity_jwt_cookie_config(new_identity_jwt))
    response.set_cookie(**get_sessionid_cookie_config(session_id))
    
    return response

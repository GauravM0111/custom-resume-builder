from typing import Annotated
from fastapi import Cookie, FastAPI, Request, Response
from fastapi.params import Depends
from fastapi.responses import RedirectResponse
from models.cookies import AuthToken
from models.users import User
from routers.oauth.google import router as google_oauth_router
from auth.auth import user_login_required
from auth.jwt_service import get_user_id_from_jwt

app = FastAPI()
app.include_router(google_oauth_router)


@app.get("/")
@user_login_required
async def read_root(token: Annotated[AuthToken, Cookie()]):
    user_id = get_user_id_from_jwt(token.identity_jwt)
    return Response(content=f"Hello, {user_id}")

@app.get("/signin")
async def sign_in():
    return RedirectResponse(google_oauth_router.url_path_for("sign_in"))

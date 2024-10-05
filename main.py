from typing import Annotated
from fastapi import Cookie, Depends, FastAPI, Request
from fastapi.responses import RedirectResponse
from models.cookies import AuthToken
from routers.oauth.google import router as google_oauth_router
from routers.users import router as users_router
from routers.resume import router as resume_router
from auth.auth import user_login_required
from auth.jwt_service import get_user_from_jwt
from sqlalchemy.orm import Session
from db.core import get_db
from settings.settings import TEMPLATES
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.include_router(google_oauth_router)
app.include_router(users_router)
app.include_router(resume_router)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
@user_login_required
async def read_root(token: Annotated[AuthToken, Cookie()], request: Request, db: Session = Depends(get_db)):
    user = get_user_from_jwt(token.identity_jwt, db)

    if not user.profile:
        return TEMPLATES.TemplateResponse("import_profile.html", {"request": request, "user": user})
    
    return TEMPLATES.TemplateResponse("generate_resume.html", {"request": request, "user": user})


@app.get("/signin")
async def sign_in():
    return RedirectResponse(google_oauth_router.url_path_for("sign_in"))

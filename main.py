from typing import Annotated, Optional
from fastapi import Cookie, FastAPI, Request
from fastapi.params import Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from auth.session_service import SessionService
from db.core import get_db
from db.resumes import get_user_resumes
from routers.oauth.google import router as google_oauth_router
from routers.users import router as users_router
from routers.resume import router as resume_router
from auth.auth import user_authentication_middleware
from settings.settings import STORAGE_PUBLIC_ACCESS_URL, TEMPLATES, UNAUTHENTICATED_ENDPOINTS
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.include_router(google_oauth_router)
app.include_router(users_router)
app.include_router(resume_router)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.middleware("http")
async def user_authentication_middleware_router(request: Request, call_next):
    if request.url.path in UNAUTHENTICATED_ENDPOINTS:
        return await call_next(request)
    
    return await user_authentication_middleware(request, call_next)


@app.get("/")
async def read_root(request: Request, db: Session = Depends(get_db)):
    resumes = get_user_resumes(request.state.user["id"], db) if request.state.user else []
    return TEMPLATES.TemplateResponse(
        "home.html",
        {
            "request": request,
            "user": request.state.user,
            "resumes": resumes,
            "storage_public_access_url": STORAGE_PUBLIC_ACCESS_URL
        }
    )


@app.get("/signin")
async def sign_in(guest_id: Optional[str] = None):
    if guest_id:
        return RedirectResponse("{}?guest_id={}".format(google_oauth_router.url_path_for("sign_in"), guest_id))
    return RedirectResponse(google_oauth_router.url_path_for("sign_in"))


@app.get("/logout")
async def logout(refresh_token: Annotated[str | None, Cookie()]):
    SessionService().delete_session(refresh_token)
    response = RedirectResponse(url="/")
    response.delete_cookie('refresh_token')
    response.delete_cookie('identity_jwt')
    return response
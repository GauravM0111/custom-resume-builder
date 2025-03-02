from typing import Annotated, Optional

from fastapi import APIRouter, Cookie, Request
from fastapi.params import Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from auth.session_service import SessionService
from db.core import get_db
from db.resumes import get_user_resumes
from routers.oauth.google import router as google_oauth_router
from settings.settings import STORAGE_PUBLIC_ACCESS_URL, TEMPLATES

router = APIRouter()


@router.get("/")
async def read_root(request: Request, db: Session = Depends(get_db)):
    resumes = (
        get_user_resumes(request.state.user["id"], db) if request.state.user else []
    )
    return TEMPLATES.TemplateResponse(
        "home.html",
        {
            "request": request,
            "user": request.state.user,
            "resumes": resumes,
            "storage_public_access_url": STORAGE_PUBLIC_ACCESS_URL,
        },
    )


@router.get("/signin")
async def sign_in(guest_id: Optional[str] = None):
    if guest_id:
        return RedirectResponse(
            "{}?guest_id={}".format(
                google_oauth_router.url_path_for("sign_in"), guest_id
            )
        )
    return RedirectResponse(google_oauth_router.url_path_for("sign_in"))


@router.get("/logout")
async def logout(refresh_token: Annotated[str | None, Cookie()]):
    SessionService().delete_session(refresh_token)
    response = RedirectResponse(url="/")
    response.delete_cookie("refresh_token")
    response.delete_cookie("identity_jwt")
    return response


@router.get("/profile")
async def profile(request: Request):
    return TEMPLATES.TemplateResponse(
        "profile.html", {"request": request, "user": request.state.user}
    )

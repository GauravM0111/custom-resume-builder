from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, Request
from sqlalchemy.orm import Session

from auth.auth import user_login_required
from auth.jwt_service import get_user_from_jwt
from db.core import get_db
from models.cookies import AuthToken
from settings.settings import TEMPLATES


router = APIRouter(prefix="/users")


@router.get("/profile")
@user_login_required
async def profile(token: Annotated[AuthToken, Cookie()], request: Request, db: Session = Depends(get_db)):
    user = get_user_from_jwt(token.identity_jwt, db)
    return TEMPLATES.TemplateResponse("profile.html", {"request": request, "user": user})

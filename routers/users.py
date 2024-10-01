from typing import Annotated
from fastapi import APIRouter, Cookie, Depends, Form, Response
from sqlalchemy.orm import Session
from auth.auth import user_login_required
from auth.jwt_service import get_user_from_jwt
from db.core import get_db
from db.users import update_user
from models.cookies import AuthToken
from models.users import UserUpdate
from services.linkedin_service import get_profile_data

router = APIRouter(prefix="/users")


@router.post("/import-profile")
@user_login_required
async def import_profile(token: Annotated[AuthToken, Cookie()], linkedin_url: Annotated[str, Form()], db: Session = Depends(get_db)):
    profile_data = get_profile_data(linkedin_url)

    user = get_user_from_jwt(token.identity_jwt, db)
    user = update_user(UserUpdate(id=user.id, profile=profile_data), db)

    response =  Response(status_code=200)
    response.headers["HX-Refresh"] = "true"
    return response


@router.post("/generate-resume")
@user_login_required
async def generate_resume(token: Annotated[AuthToken, Cookie()], job_description: Annotated[str, Form()], db: Session = Depends(get_db)):
    user = get_user_from_jwt(token.identity_jwt, db)
    resume_data = generate_resume(user.profile, job_description)
    user = update_user(UserUpdate(id=user.id, resume=resume_data), db)

    response =  Response(status_code=200)
    response.headers["HX-Refresh"] = "true"
    return response

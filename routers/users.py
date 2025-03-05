from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request, Response, status
from sqlalchemy.orm import Session

from auth.auth import login_user_in_response
from db.core import NotFoundError, get_db
from db.profiles import get_profile as get_profile_db
from db.users import update_user as update_user_db
from models.users import UserUpdate
from services.profile_service import ProfileService
from services.user_service import UserService
from settings.settings import TEMPLATES

router = APIRouter(prefix="/user")


@router.get("/profile")
async def profile(request: Request, db: Session = Depends(get_db)):
    if not request.state.user:
        return TEMPLATES.TemplateResponse(
            "profile.html",
            {"request": request, "user": {}, "profile": {}},
        )

    if not request.state.user.get("profile_id"):
        return TEMPLATES.TemplateResponse(
            "profile.html",
            {"request": request, "user": request.state.user, "profile": {}},
        )

    try:
        profile = get_profile_db(request.state.user["profile_id"], db)
    except NotFoundError:
        return TEMPLATES.TemplateResponse(
            "profile.html",
            {"request": request, "user": request.state.user, "profile": {}},
        )

    time_ago = datetime.now(timezone.utc) - profile.updated_at

    if time_ago.days > 365:
        years = time_ago.days // 365
        if years == 1:
            time_ago = "1 year ago"
        else:
            time_ago = f"{years} years ago"
    elif time_ago.days >= 31:
        months = time_ago.days // 31
        if months == 1:
            time_ago = "1 month ago"
        else:
            time_ago = f"{months} months ago"
    elif time_ago.days > 1:
        time_ago = f"{time_ago.days} days ago"
    elif time_ago.days == 1:
        time_ago = "1 day ago"
    elif time_ago.seconds >= (60 * 60):
        hours = time_ago.seconds // (60 * 60)
        if hours == 1:
            time_ago = "1 hour ago"
        else:
            time_ago = f"{hours} hours ago"
    elif time_ago.seconds >= 60:
        minutes = time_ago.seconds // 60
        if minutes == 1:
            time_ago = "1 minute ago"
        else:
            time_ago = f"{time_ago.seconds // 60} minutes ago"
    else:
        time_ago = "just now"

    profile = profile.model_dump()
    profile["time_ago"] = time_ago

    return TEMPLATES.TemplateResponse(
        "profile.html",
        {"request": request, "user": request.state.user, "profile": profile},
    )


@router.put("/profile")
async def update_profile(
    request: Request,
    linkedin_url: Annotated[str, Form()],
    db: Session = Depends(get_db),
):
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    response.headers["HX-Redirect"] = f"/user/profile"

    profile = ProfileService().create_or_update_profile(linkedin_url, db)

    if request.state.user:
        update_user_db(
            UserUpdate(id=request.state.user["id"], profile_id=profile.id), db
        )
        response.delete_cookie(
            "identity_jwt"
        )  # since profile is imported, we need to update the jwt
    else:
        user = UserService().create_guest_user(db)
        user = update_user_db(UserUpdate(id=user.id, profile_id=profile.id), db)
        response = await login_user_in_response(response, user)

    return response

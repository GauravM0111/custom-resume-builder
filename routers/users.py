from fastapi import APIRouter, Request

from settings.settings import TEMPLATES

router = APIRouter(prefix="/users")


@router.get("/profile")
async def profile(request: Request):
    return TEMPLATES.TemplateResponse(
        "profile.html", {"request": request, "user": request.state.user}
    )

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session

from auth.auth import login_user_in_response
from db.core import get_db
from db.users import get_user_profile, update_user
from db.resumes import get_resume, get_user_resumes
from models.resumes import JobDetails
from models.users import User, UserUpdate
from services.profile_service import ProfileService
from services.resume_service import ResumeService
from services.user_service import UserService
from settings.settings import TEMPLATES


router = APIRouter(prefix="/resume")


@router.get("/import-profile")
async def import_profile_page(request: Request, redirect: Optional[str] = None):
    return TEMPLATES.TemplateResponse("import_profile.html", {"request": request, "user": request.state.user, "redirect": redirect})


@router.post("/import-profile")
async def import_profile(linkedin_url: Annotated[str, Form()], request: Request, redirect: Optional[str] = None, db: Session = Depends(get_db)):
    response = Response(status_code=200)
    profile_data = ProfileService().get_linkedin_profile(linkedin_url)

    if request.state.user:
        user = update_user(UserUpdate(id=request.state.user["id"], profile=profile_data), db)
        response.delete_cookie(key="identity_jwt")  # since profile is imported, we need to update the jwt
    else:
        user = UserService().create_guest_user(db)
        user = update_user(UserUpdate(id=user.id, profile=profile_data), db)
        response = await login_user_in_response(response, user)

    response.headers["HX-Redirect"] = redirect or "/"
    return response


@router.get("/generate")
async def generate_resume_page(request: Request):
    if not request.state.user or not request.state.user["profile"]:
        return RedirectResponse(url="/resume/import-profile?redirect=/resume/generate")

    return TEMPLATES.TemplateResponse("generate_resume.html", {"request": request, "user": request.state.user})


@router.post("/generate")
async def generate_resume(job_details: Annotated[JobDetails, Form()], request: Request, db: Session = Depends(get_db)):
    user = dict(request.state.user).copy()
    user["profile"] = get_user_profile(request.state.user["id"], db)
    user = User(**user)

    resume = await ResumeService().save_resume(
        resume = await ResumeService().generate_resume(user, job_details.description),
        user_id = user.id,
        job_description = job_details.description,
        job_title = job_details.title,
        db = db
    )

    response = Response(status_code=200)
    response.headers["HX-Redirect"] = f"/resume/render/{resume.id}"
    return response


@router.get("/render/{resume_id}")
async def render_resume(resume_id: str, request: Request, db: Session = Depends(get_db)):
    resume = get_resume(resume_id, db)

    if resume.user_id != request.state.user["id"]:
        raise HTTPException(status_code=403, detail="Forbidden")

    resume_html = await ResumeService().render_resume(resume.resume)
    return HTMLResponse(content=resume_html)


@router.get("/history")
async def resume_history(request: Request, db: Session = Depends(get_db)):
    if not request.state.user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    resumes = get_user_resumes(request.state.user["id"], db)
    return TEMPLATES.TemplateResponse("resumes.html", {"request": request, "user": request.state.user, "resumes": resumes})


@router.get("/history/{resume_id}")
async def view_resume(resume_id: str, request: Request):
    return TEMPLATES.TemplateResponse("resume.html", {"request": request, "user": request.state.user})

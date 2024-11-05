from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session

from db.core import get_db
from db.users import get_user_profile, update_user
from db.resumes import create_resume, get_resume
from models.jobs import JobForm
from models.resumes import CreateResume
from models.users import User, UserUpdate
from services.job_service import JobService
from services.profile_service import ProfileService
from services.resume_service import ResumeService
from settings.settings import TEMPLATES


router = APIRouter(prefix="/resume")


@router.get("/import-profile")
async def import_profile_page(request: Request, redirect: Optional[str] = None):
    return TEMPLATES.TemplateResponse("import_profile.html", {"request": request, "user": request.state.user, "redirect": redirect})


@router.post("/import-profile")
async def import_profile(linkedin_url: Annotated[str, Form()], request: Request, redirect: Optional[str] = None, db: Session = Depends(get_db)):
    profile_data = ProfileService().get_linkedin_profile(linkedin_url)
    update_user(UserUpdate(id=request.state.user["id"], profile=profile_data), db)

    response = Response(status_code=200)
    response.delete_cookie(key="identity_jwt")  # since profile is imported, we need to update the jwt
    response.headers["HX-Redirect"] = redirect or "/"
    return response


@router.get("/generate")
async def generate_resume_page(request: Request):
    if not request.state.user["profile"]:
        return RedirectResponse(url="/resume/import-profile?redirect=/resume/generate")

    return TEMPLATES.TemplateResponse("generate_resume.html", {"request": request, "user": request.state.user})


@router.post("/generate")
async def generate_resume(job_form: Annotated[JobForm, Form()], request: Request, db: Session = Depends(get_db)):
    user = dict(request.state.user).copy()
    user["profile"] = get_user_profile(request.state.user["id"], db)
    user = User(**user)

    job = JobService().create_job(job_form, db)

    resume = create_resume(
        CreateResume(
            user_id = user.id,
            job_id = job.id,
            resume = await ResumeService().generate_resume(user, job)
        ),
        db
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
async def resume_history(request: Request):
    return TEMPLATES.TemplateResponse("resumes.html", {"request": request})


@router.get("/history/{resume_id}")
async def view_resume(resume_id: str, request: Request):
    return TEMPLATES.TemplateResponse("resume.html", {"request": request})

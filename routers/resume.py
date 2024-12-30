import json
from typing import Annotated, Optional
import io

from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse, HTMLResponse, StreamingResponse
from sqlalchemy.orm import Session

from auth.auth import login_user_in_response
from db.core import get_db
from db.users import get_user_profile, update_user
from db.resumes import get_resume, update_resume as update_resume_db
from models.resumes import JobDetails, UpdateResume, UpdateResumeForm
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
    if not request.state.user:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    user = dict(request.state.user).copy()
    user["profile"] = get_user_profile(request.state.user["id"], db)
    user = User(**user)

    try:
        resume = await ResumeService().generate_resume(user, job_details.description)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    resume = await ResumeService().save_resume(
        resume=resume,
        user_id=user.id,
        job_description=job_details.description,
        job_title=job_details.title,
        db=db
    )

    response = Response(status_code=200)
    response.headers["HX-Redirect"] = f"/resume/preview/{resume.id}"
    return response


@router.get("/preview/{resume_id}")
async def preview_resume(resume_id: str, request: Request, db: Session = Depends(get_db)):
    resume = get_resume(resume_id, db)

    if not request.state.user or resume.user_id != request.state.user["id"]:
        raise HTTPException(status_code=403, detail="Forbidden")

    resume_html = await ResumeService().render_resume(resume)
    return HTMLResponse(content=resume_html)


@router.get("/pdf/{resume_id}")
async def download_resume_pdf(resume_id: str, request: Request, download: bool = False, db: Session = Depends(get_db)):
    resume = get_resume(resume_id, db)

    if not request.state.user or resume.user_id != request.state.user["id"]:
        raise HTTPException(status_code=403, detail="Forbidden")

    pdf_bytes = await ResumeService().generate_pdf(resume)

    response = StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf"
    )

    if download:
        response.headers["Content-Disposition"] = f"attachment; filename={resume.job_title}-resume.pdf"
    else:
        response.headers["Content-Disposition"] = f"inline; filename={resume.job_title}-resume.pdf"

    return response


@router.get("/{resume_id}/edit")
async def edit_resume(resume_id: str, request: Request, db: Session = Depends(get_db)):
    resume = get_resume(resume_id, db)

    if not request.state.user or resume.user_id != request.state.user["id"]:
        raise HTTPException(status_code=403, detail="Forbidden")

    return TEMPLATES.TemplateResponse("edit_resume.html", {"request": request, "resume": resume, "user": request.state.user})


@router.patch("/{resume_id}")
async def update_resume(resume_id: str, update_form: Annotated[UpdateResumeForm, Form()], db: Session = Depends(get_db)):
    update_form = update_form.model_dump(exclude_none=True)

    if len(update_form) == 0:
        response = Response(status_code=status.HTTP_204_NO_CONTENT)
    else:
        if 'resume' in update_form:
            update_form["resume"] = json.loads(update_form["resume"])

        update_resume_db(UpdateResume(id=resume_id, **update_form), db)
        response = Response(status_code=status.HTTP_200_OK)

    response.headers["HX-Redirect"] = f"/resume/{resume_id}/edit"
    return response

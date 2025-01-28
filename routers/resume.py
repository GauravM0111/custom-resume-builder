import json
from typing import Annotated, Optional
import io

from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse, HTMLResponse, StreamingResponse
from sqlalchemy.orm import Session

from auth.auth import login_user_in_response
from db.core import get_db
from db.users import get_user_profile, update_user
from db.resumes import get_resume
from models.resumes import CreateResume, JobDetails, UpdateResume, UpdateResumeForm
from models.users import User, UserUpdate
from services.llm_service import LLMService
from services.profile_service import ProfileService
from services.resume_service import ResumeService
from services.user_service import UserService
from settings.settings import STORAGE_PUBLIC_ACCESS_URL, TEMPLATES


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
        resume = await LLMService().generate_resume(user, job_details.description)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    resume = await ResumeService().save_resume(
        db=db,
        create_resume_object=CreateResume(
            resume=resume,
            user_id=user.id,
            job_title=job_details.title,
            job_description=job_details.description
        )
    )

    response = Response(status_code=200)
    response.headers["HX-Redirect"] = f"/resume/{resume.id}/edit"
    return response


@router.get("/{resume_id}/pdf")
async def resume_pdf(resume_id: str, download: bool = False, db: Session = Depends(get_db)):
    resume = get_resume(resume_id, db)

    pdf_bytes, _ = await ResumeService().generate_pdf_and_img(resume)

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": "{}; filename={}-resume.pdf".format(
                'attachment' if download else 'inline',
                resume.job_title.replace(" ", "_")
            )
        }
    )


@router.get("/{resume_id}/edit")
async def edit_resume(resume_id: str, request: Request, db: Session = Depends(get_db)):
    resume = get_resume(resume_id, db)

    if not request.state.user or resume.user_id != request.state.user["id"]:
        raise HTTPException(status_code=403, detail="Forbidden")

    return TEMPLATES.TemplateResponse(
        "edit_resume/index.html",
        {
            "request": request,
            "resume": resume,
            "user": request.state.user,
            "storage_public_access_url": STORAGE_PUBLIC_ACCESS_URL
        }
    )


@router.patch("/{resume_id}")
async def update_resume(resume_id: str, update_form: Annotated[UpdateResumeForm, Form()], db: Session = Depends(get_db)):
    update_form = update_form.model_dump(exclude_none=True)

    if len(update_form) == 0:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    if 'resume' in update_form:
        update_form["resume"] = json.loads(update_form["resume"])
        resume = await ResumeService().update_resume(db, UpdateResume(id=resume_id, **update_form))

        return HTMLResponse(
            content=f'''
                <object
                    id="resumePdfPreview"
                    data="/resume/{resume.id}/pdf"
                    type="application/pdf"
                    class="bg-white w-full h-full shadow-lg rounded-lg"
                ></object>
            ''',
            status_code=200
        )

    resume = await ResumeService().update_resume(db, UpdateResume(id=resume_id, **update_form))
    return Response(
        content=resume.job_title,
        status_code=status.HTTP_200_OK
    )

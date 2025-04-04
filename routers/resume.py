import io
import json
import traceback
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from sqlalchemy.orm import Session

from auth.auth import login_user_in_response
from db.core import get_db
from db.resumes import delete_resume as delete_resume_db
from db.resumes import get_resume
from db.users import update_user
from models.resumes import (
    CreateResume,
    JobDetails,
    Resume,
    Theme,
    UpdateResume,
    UpdateResumeForm,
)
from models.users import User, UserUpdate
from services.llm_service import LLMService
from services.profile_service import Profile, ProfileService
from services.resume_service import ResumeService
from services.user_service import UserService
from settings.settings import STORAGE_PUBLIC_ACCESS_URL, TEMPLATES

router = APIRouter(prefix="/resume")


@router.get("/import-profile")
async def import_profile_page(request: Request, redirect: Optional[str] = None):
    return TEMPLATES.TemplateResponse(
        "import_profile.html",
        {"request": request, "user": request.state.user, "redirect": redirect},
    )


@router.post("/import-profile")
async def import_profile(
    linkedin_url: Annotated[str, Form()],
    request: Request,
    redirect: Optional[str] = None,
    db: Session = Depends(get_db),
):
    response = Response(status_code=200)
    profile: Profile = ProfileService().create_or_update_profile(linkedin_url, db)

    if request.state.user:
        user = update_user(
            UserUpdate(id=request.state.user["id"], profile_id=profile.id), db
        )
        response.delete_cookie(
            key="identity_jwt"
        )  # since profile is imported, we need to update the jwt
    else:
        user = UserService().create_guest_user(db)
        user = update_user(UserUpdate(id=user.id, profile_id=profile.id), db)
        response = await login_user_in_response(response, user)

    response.headers["HX-Redirect"] = redirect or "/"
    return response


@router.get("/generate")
async def generate_resume_page(request: Request):
    if not request.state.user or not request.state.user["profile_id"]:
        return RedirectResponse(url="/resume/import-profile?redirect=/resume/generate")

    return TEMPLATES.TemplateResponse(
        "generate_resume.html", {"request": request, "user": request.state.user}
    )


@router.post("/generate")
async def generate_resume(
    job_details: Annotated[JobDetails, Form()],
    request: Request,
    db: Session = Depends(get_db),
):
    if not request.state.user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access resume",
        )

    try:
        resume = await LLMService().generate_resume(
            User(**request.state.user), job_details.description, db
        )
    except ValueError as e:
        traceback.print_exception(e)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        traceback.print_exception(e)
        raise HTTPException(status_code=500, detail=str(e))

    resume = await ResumeService().save_resume(
        db=db,
        create_resume_object=CreateResume(
            resume=resume,
            user_id=request.state.user["id"],
            job_title=job_details.title,
            job_description=job_details.description,
        ),
    )

    response = Response(status_code=200)
    response.headers["HX-Redirect"] = f"/resume/{resume.id}/edit"
    return response


def current_user_has_access(request: Request, resume: Resume):
    return request.state.user and resume.user_id == request.state.user["id"]


@router.get("/{resume_id}/pdf")
async def resume_pdf(
    resume_id: str,
    request: Request,
    download: bool = False,
    db: Session = Depends(get_db),
):
    resume = get_resume(resume_id, db)

    if not current_user_has_access(request, resume):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access resume",
        )

    pdf_bytes, _ = await ResumeService().generate_pdf_and_img(resume)

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": "{}; filename={}-resume.pdf".format(
                "attachment" if download else "inline",
                resume.job_title.replace(" ", "_"),
            )
        },
    )


@router.get("/{resume_id}/edit")
async def edit_resume(resume_id: str, request: Request, db: Session = Depends(get_db)):
    resume = get_resume(resume_id, db)

    if not current_user_has_access(request, resume):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access resume",
        )

    return TEMPLATES.TemplateResponse(
        "edit_resume/index.html",
        {
            "request": request,
            "resume": resume,
            "themes": [theme.name for theme in Theme],
            "user": request.state.user,
            "storage_public_access_url": STORAGE_PUBLIC_ACCESS_URL,
        },
    )


@router.patch("/{resume_id}")
async def update_resume(
    resume_id: str,
    request: Request,
    update_form: Annotated[UpdateResumeForm, Form()],
    db: Session = Depends(get_db),
):
    resume = get_resume(resume_id, db)

    if not current_user_has_access(request, resume):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access resume",
        )

    update_form = update_form.model_dump(exclude_none=True)

    if len(update_form) == 0:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    if "resume" not in update_form and "theme" not in update_form:
        resume = await ResumeService().update_resume(
            db, UpdateResume(id=resume_id, **update_form)
        )
        return Response(content=resume.job_title, status_code=status.HTTP_200_OK)

    if "resume" in update_form:
        update_form["resume"] = json.loads(update_form["resume"])
    if "theme" in update_form:
        update_form["theme"] = Theme[update_form["theme"]]

    resume = await ResumeService().update_resume(
        db, UpdateResume(id=resume_id, **update_form)
    )

    return HTMLResponse(
        content=f"""
            <object
                id="resumePdfPreview"
                data="/resume/{resume.id}/pdf"
                type="application/pdf"
                class="bg-white w-full h-full shadow-lg rounded-lg"
            ></object>
        """,
        status_code=200,
    )


@router.delete("/{resume_id}")
async def delete_resume(
    resume_id: str, request: Request, db: Session = Depends(get_db)
):
    resume = get_resume(resume_id, db)

    if not current_user_has_access(request, resume):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access resume",
        )

    if not delete_resume_db(resume_id, db):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resume doesn't exist"
        )

    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    response.headers["HX-Redirect"] = "/"
    return response

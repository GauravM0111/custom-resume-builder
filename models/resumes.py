from datetime import datetime
from pydantic import BaseModel


class Resume(BaseModel):
    id: str
    user_id: str
    job_title: str
    job_description: str
    resume: dict
    created_at: datetime

class CreateResume(BaseModel):
    user_id: str
    job_title: str
    job_description: str
    resume: dict

class UpdateResume(BaseModel):
    id: str
    job_title: str | None = None
    job_description: str | None = None
    resume: dict | None = None

class UpdateResumeForm(BaseModel):
    job_title: str | None = None
    job_description: str | None = None
    resume: str | None = None

class JobDetails(BaseModel):
    title: str | None = None
    description: str

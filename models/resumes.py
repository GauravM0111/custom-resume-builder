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

class JobDetails(BaseModel):
    title: str | None = None
    description: str

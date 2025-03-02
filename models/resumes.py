from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class Theme(Enum):
    EVEN = "jsonresume-theme-even"
    STRAIGHTFORWARD = "jsonresume-theme-straightforward"
    MODERN = "jsonresume-theme-modern-extended"
    CORA = "jsonresume-theme-cora"


class Resume(BaseModel):
    id: str
    user_id: str
    job_title: str
    job_description: str
    resume: dict
    theme: Theme
    created_at: datetime


class CreateResume(BaseModel):
    user_id: str
    job_title: str
    job_description: str
    resume: dict
    theme: Theme | None = Theme.EVEN


class UpdateResume(BaseModel):
    id: str
    job_title: str | None = None
    job_description: str | None = None
    resume: dict | None = None
    theme: Theme | None = None


class UpdateResumeForm(BaseModel):
    job_title: str | None = None
    job_description: str | None = None
    resume: str | None = None
    theme: str | None = None


class JobDetails(BaseModel):
    title: str | None = None
    description: str

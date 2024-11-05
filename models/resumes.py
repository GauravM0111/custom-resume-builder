from pydantic import BaseModel


class Resume(BaseModel):
    id: str
    user_id: str
    job_id: str
    resume: dict

class CreateResume(BaseModel):
    user_id: str
    job_id: str
    resume: dict

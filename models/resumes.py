from pydantic import BaseModel


class Resume(BaseModel):
    user_id: str
    job_id: str
    resume: dict

from pydantic import BaseModel


class Job(BaseModel):
    id: str
    title: str
    description: str


class JobForm(BaseModel):
    title: str | None = None
    description: str


class JobCreate(BaseModel):
    title: str
    description: str

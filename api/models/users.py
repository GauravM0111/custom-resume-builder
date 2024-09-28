from pydantic import BaseModel
from datetime import datetime


class User(BaseModel):
    id: str
    email: str
    created_at: datetime
    name: str | None = None
    picture: str | None = None
    profile_file_id: str | None = None

class UserCreate(BaseModel):
    email: str
    created_at: datetime | None = None
    name: str | None = None
    picture: str | None = None
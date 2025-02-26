from pydantic import BaseModel
from datetime import datetime


class User(BaseModel):
    id: str
    email: str
    created_at: datetime
    is_guest: bool
    name: str | None = None
    picture: str | None = None
    profile_id: str | None = None

class UserCreate(BaseModel):
    email: str
    is_guest: bool = False
    name: str | None = None
    picture: str | None = None
    profile_id: str | None = None

class UserUpdate(BaseModel):
    id: str
    email: str | None = None
    is_guest: bool | None = None
    name: str | None = None
    picture: str | None = None
    profile_id: str | None = None

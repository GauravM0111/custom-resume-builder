from datetime import datetime
from pydantic import BaseModel


class Profile(BaseModel):
    id: str
    profile: dict
    url: str
    updated_at: datetime

class CreateProfile(BaseModel):
    profile: dict
    url: str

class UpdateProfile(BaseModel):
    id: str
    profile: dict

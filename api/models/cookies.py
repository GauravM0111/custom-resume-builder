from pydantic import BaseModel


class Cookies(BaseModel):
    identity_jwt: str | None = None
    refresh_token: str | None = None

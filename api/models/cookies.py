from pydantic import BaseModel


class AuthToken(BaseModel):
    identity_jwt: str | None = None
    refresh_token: str | None = None

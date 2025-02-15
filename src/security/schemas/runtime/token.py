from pydantic import BaseModel


class TokenSession(BaseModel):
    sub: str | None = None
    username: str | None = None
    auth_type: str | None = None

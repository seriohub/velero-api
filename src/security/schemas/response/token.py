from pydantic import BaseModel


class TokenRefresh(BaseModel):
    access_token: str
    token_type: str


class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str

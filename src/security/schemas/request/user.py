from pydantic import BaseModel


class UserIn(BaseModel):
    username: str
    password: str


class UserCreate(BaseModel):
    username: str
    full_name: str | None = None
    password: str
    is_admin: bool = False


class UserUPDPassword(BaseModel):
    password: str

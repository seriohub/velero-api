# to get a string like this run:
# openssl rand -hex 32
from pydantic import BaseModel
from pydantic.v1 import BaseSettings
import uuid
from helpers.printer_helper import PrintHelper

print_ls = PrintHelper('[lib.model]')


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


# class User(BaseModel):
#     id: int
#     username: str
#     full_name: str | None = None
#     password: str
#     is_default: bool
#     is_disabled: bool


class UserIn(BaseModel):
    username: str
    password: str


class UserCreate(BaseModel):
    username: str
    full_name: str | None = None
    password: str
    is_admin: bool=False


class UserUPDPassword(BaseModel):
    password: str


class UserOut(BaseModel):
    id: uuid.UUID
    username: str
    is_admin: bool
    is_default: bool
    is_disabled: bool


class Settings(BaseSettings):
    app_name: str = 'FastAPI'
    admin_email: str

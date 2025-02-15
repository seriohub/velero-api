import uuid

from pydantic import BaseModel


class UserOut(BaseModel):
    id: uuid.UUID
    username: str
    is_admin: bool
    is_default: bool
    is_disabled: bool

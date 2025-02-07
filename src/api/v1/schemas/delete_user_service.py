from pydantic import BaseModel


class DeleteUserService(BaseModel):
    config: str

from pydantic import BaseModel


class CreateUserService(BaseModel):
    config: str

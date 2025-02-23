from pydantic import BaseModel


class CreateUserServiceRequestSchema(BaseModel):
    config: str

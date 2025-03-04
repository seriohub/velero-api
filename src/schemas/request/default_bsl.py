from pydantic import BaseModel


class DefaultBslRequestSchema(BaseModel):
    name: str
    default: bool = True

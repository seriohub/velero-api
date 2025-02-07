from pydantic import BaseModel


class DefaultBsl(BaseModel):
    name: str
    default: bool = True

from pydantic import BaseModel

class DeleteBsl(BaseModel):
    resourceName: str

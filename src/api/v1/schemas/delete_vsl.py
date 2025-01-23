from pydantic import BaseModel

class DeleteVsl(BaseModel):
    resourceName: str

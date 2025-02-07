from pydantic import BaseModel


class DeleteRestore(BaseModel):
    resourceName: str

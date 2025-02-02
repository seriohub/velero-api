from pydantic import BaseModel


class DeleteBackup(BaseModel):
    resourceName: str

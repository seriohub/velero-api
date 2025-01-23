from pydantic import BaseModel

class DeleteSchedule(BaseModel):
    resourceName: str

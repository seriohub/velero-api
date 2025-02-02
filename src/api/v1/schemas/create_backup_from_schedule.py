from pydantic import BaseModel


class CreateBackupFromSchedule(BaseModel):
    scheduleName: str

from pydantic import BaseModel


class CreateBackupFromScheduleRequestSchema(BaseModel):
    scheduleName: str

from pydantic import BaseModel, Field

class PauseScheduleRequestSchema(BaseModel):
    name: str = Field(..., description="The name of the resource.")

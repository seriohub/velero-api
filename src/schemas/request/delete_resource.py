from pydantic import BaseModel, Field

class DeleteResourceRequestSchema(BaseModel):
    name: str = Field(..., description="The name of the resource.")

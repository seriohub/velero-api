from pydantic import BaseModel


class AppriseTestServiceRequestSchema(BaseModel):
    config: str

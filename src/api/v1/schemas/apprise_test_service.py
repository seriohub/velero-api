from pydantic import BaseModel


class AppriseTestService(BaseModel):
    config: str

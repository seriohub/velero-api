from typing import Dict
from pydantic import BaseModel, Field


class FailedRequest(BaseModel):
    error: Dict[str, str] = Field(default_factory=lambda: {"title": "", "description": ""})

    def __init__(self, title: str = "", description: str = ""):
        super().__init__(
            error={"title": title,
                   "description": description},
        )

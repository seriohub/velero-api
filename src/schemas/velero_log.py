from typing import List, Optional
from pydantic import BaseModel


class VeleroLog(BaseModel):
    logs: Optional[List[str]] = None

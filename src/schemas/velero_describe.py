from typing import Dict, Optional
from pydantic import BaseModel


class VeleroDescribe(BaseModel):
    details: Optional[Dict] = None

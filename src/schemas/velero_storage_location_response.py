from typing import Optional, Dict
from pydantic import BaseModel


class VeleroStorageLocation(BaseModel):
    success: bool
    storage_info: Optional[Dict] = None
    error: Optional[str] = None

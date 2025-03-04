from typing import List, Dict, Optional
from pydantic import BaseModel


class VeleroStorageClass(BaseModel):
    storage_classes: Optional[List[Dict]] = None

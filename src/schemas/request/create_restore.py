from typing import Optional, Dict

from pydantic import BaseModel
from configs.config_boot import config_app


class CreateRestoreRequestSchema(BaseModel):
    name: str
    namespace: Optional[str] = config_app.get_k8s_velero_namespace()

    # spec
    backupName: str
    namespaceMapping: Optional[Dict[str, str]] = None

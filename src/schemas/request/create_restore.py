from pydantic import BaseModel
from typing import Optional, Dict, List
from vui_common.configs.config_proxy import config_app


class CreateRestoreRequestSchema(BaseModel):
    name: str
    namespace: Optional[str] = config_app.k8s.velero_namespace

    # spec
    backupName: Optional[str]
    scheduleName: Optional[str]
    itemOperationTimeout: Optional[str] = "4h"
    namespaceMapping: Optional[Dict[str, str]] = None
    includedNamespaces: Optional[List[str]] = None
    excludedNamespaces: Optional[List[str]] = None
    includedResources: Optional[List[str]] = None
    excludedResources: Optional[List[str]] = None

    includeClusterResources: Optional[bool] = None
    restorePVs: Optional[bool] = True
    preserveNodePorts: Optional[bool] = True
    # existingResourcePolicy: Optional[bool] = True

    # spec child
    labelSelector: Optional[Dict[str, str]] = None
    writeSparseFiles: Optional[bool] = True

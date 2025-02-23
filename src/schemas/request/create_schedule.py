from typing import Optional, Dict

from pydantic import BaseModel
from configs.config_boot import config_app


class CreateScheduleRequestSchema(BaseModel):
    name: str
    namespace: Optional[str] = config_app.get_k8s_velero_namespace()

    # spec
    schedule: str

    # spec.template
    includedNamespaces: list
    excludedNamespaces: list
    includedResources: list
    excludedResources: list
    ttl: str
    snapshotVolumes: bool
    includeClusterResources: bool
    defaultVolumesToFsBackup: bool
    storageLocation: str
    volumeSnapshotLocations: list

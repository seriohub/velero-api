from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from enum import Enum

# ------------------- SCHEDULE STATUS -------------------
class SchedulePhase(str, Enum):
    NEW = "New"
    ENABLED = "Enabled"
    FAILED_VALIDATION = "FailedValidation"

class ScheduleStatus(BaseModel):
    phase: Optional[SchedulePhase] = None
    lastBackup: Optional[str] = None
    validationErrors: Optional[List[str]] = None

# ------------------- HOOKS & RESOURCE HOOKS -------------------
class HookExec(BaseModel):
    container: Optional[str] = None
    command: List[str]
    onError: Optional[str] = "Fail"
    timeout: Optional[str] = "30s"

class HookResource(BaseModel):
    name: str
    includedNamespaces: Optional[List[str]] = None
    excludedNamespaces: Optional[List[str]] = None
    includedResources: List[str]
    excludedResources: Optional[List[str]] = None
    labelSelector: Optional[Dict[str, Dict[str, str]]] = None
    pre: Optional[List[Dict[str, HookExec]]] = None
    post: Optional[List[Dict[str, HookExec]]] = None

class Hooks(BaseModel):
    resources: Optional[List[HookResource]] = None

# ------------------- BACKUP TEMPLATE -------------------
class BackupTemplate(BaseModel):
    csiSnapshotTimeout: Optional[str] = "10m"
    resourcePolicy: Optional[Dict[str, str]] = None
    includedNamespaces: Optional[List[str]] = None
    excludedNamespaces: Optional[List[str]] = None
    includedResources: Optional[List[str]] = None
    excludedResources: Optional[List[str]] = None
    orderedResources: Optional[Dict[str, List[str]]] = None
    includeClusterResources: Optional[bool] = None
    excludedClusterScopedResources: Optional[List[str]] = None
    includedClusterScopedResources: Optional[List[str]] = None
    excludedNamespaceScopedResources: Optional[List[str]] = None
    includedNamespaceScopedResources: Optional[List[str]] = None
    labelSelector: Optional[Dict[str, Dict[str, str]]] = None
    orLabelSelectors: Optional[List[Dict[str, Dict[str, str]]]] = None
    snapshotVolumes: Optional[bool] = None
    storageLocation: Optional[str] = None
    volumeSnapshotLocations: Optional[List[str]] = None
    ttl: Optional[str] = "24h"
    defaultVolumesToFsBackup: Optional[bool] = None
    snapshotMoveData: Optional[bool] = None
    datamover: Optional[str] = None
    uploaderConfig: Optional[Dict[str, int]] = None
    metadata: Optional[Dict[str, Any]] = None
    hooks: Optional[Hooks] = None

# ------------------- SCHEDULE SPEC -------------------
class ScheduleSpec(BaseModel):
    paused: Optional[bool] = False
    schedule: str
    useOwnerReferencesInBackup: Optional[bool] = False
    template: BackupTemplate

# ------------------- METADATA -------------------
class ScheduleMetadata(BaseModel):
    name: str
    namespace: str
    labels: Optional[Dict[str, str]] = None
    annotations: Optional[Dict[str, str]] = None

    class Config:
        extra = "allow"

# ------------------- SCHEDULE RESPONSE -------------------
class ScheduleResponseSchema(BaseModel):
    apiVersion: str = "velero.io/v1"
    kind: str = "Schedule"
    metadata: ScheduleMetadata
    spec: ScheduleSpec
    status: Optional[ScheduleStatus] = None

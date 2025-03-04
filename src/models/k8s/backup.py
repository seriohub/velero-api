from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from enum import Enum


# BACKUP STATUS
class BackupPhase(str, Enum):
    NEW = "New"
    FAILED_VALIDATION = "FailedValidation"
    IN_PROGRESS = "InProgress"
    WAITING_FOR_PLUGIN_OPERATIONS = "WaitingForPluginOperations"
    WAITING_FOR_PLUGIN_OPERATIONS_PARTIALLY_FAILED = "WaitingForPluginOperationsPartiallyFailed"
    FINALIZING_AFTER_PLUGIN_OPERATIONS = "FinalizingafterPluginOperations"
    FINALIZING_PARTIALLY_FAILED = "FinalizingPartiallyFailed"
    COMPLETED = "Completed"
    PARTIALLY_FAILED = "PartiallyFailed"
    FAILED = "Failed"
    DELETING = "Deleting"


# BACKUP RESOURCE POLICY
class ResourcePolicy(BaseModel):
    kind: str
    name: str


# LABEL SELECTOR
class LabelSelector(BaseModel):
    matchLabels: Optional[Dict[str, str]] = None


# BACKUP SPEC
class BackupSpec(BaseModel):
    csiSnapshotTimeout: Optional[str] = "10m"
    itemOperationTimeout: Optional[str] = "4h"
    resourcePolicy: Optional[ResourcePolicy] = None
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
    labelSelector: Optional[LabelSelector] = None
    orLabelSelectors: Optional[List[LabelSelector]] = None
    snapshotVolumes: Optional[bool] = None
    storageLocation: Optional[str] = None
    volumeSnapshotLocations: Optional[List[str]] = None
    ttl: Optional[str] = "24h0m0s"
    defaultVolumesToFsBackup: Optional[bool] = None
    snapshotMoveData: Optional[bool] = None
    datamover: Optional[str] = "velero"
    uploaderConfig: Optional[Dict[str, int]] = None
    hooks: Optional[Dict[str, List[Dict[str, str]]]] = None


# BACKUP METADATA
class BackupMetadata(BaseModel):
    name: str
    namespace: str
    uid: Optional[str] = None
    resourceVersion: Optional[str] = None
    generation: Optional[int] = None
    creationTimestamp: Optional[str] = None
    labels: Optional[Dict[str, str]] = None
    annotations: Optional[Dict[str, str]] = None
    managedFields: Optional[List[Dict[str, Any]]] = None

    class Config:
        extra = "allow"


# BACKUP STATUS
class BackupStatus(BaseModel):
    version: Optional[int] = 1
    expiration: Optional[str] = None
    phase: Optional[BackupPhase] = None
    validationErrors: Optional[List[str]] = None
    startTimestamp: Optional[str] = None
    completionTimestamp: Optional[str] = None
    volumeSnapshotsAttempted: Optional[int] = 0
    volumeSnapshotsCompleted: Optional[int] = 0
    backupItemOperationsAttempted: Optional[int] = 0
    backupItemOperationsCompleted: Optional[int] = 0
    backupItemOperationsFailed: Optional[int] = 0
    warnings: Optional[int] = 0
    errors: Optional[int] = 0
    failureReason: Optional[str] = None
    resourceList: Optional[Dict] = None

    class Config:
        extra = "allow"


# BACKUP RESPONSE
class BackupResponseSchema(BaseModel):
    apiVersion: str = "velero.io/v1"
    kind: str = "Backup"
    metadata: BackupMetadata
    spec: Optional[BackupSpec] = None
    status: Optional[BackupStatus] = None

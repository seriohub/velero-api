from typing import Literal, Optional, List, Dict, Any
from pydantic import BaseModel


# RESTORE STATUS
class RestoreStatus(str):
    NEW = "New"
    FAILED_VALIDATION = "FailedValidation"
    IN_PROGRESS = "InProgress"
    WAITING_FOR_PLUGIN_OPERATIONS = "WaitingForPluginOperations"
    WAITING_FOR_PLUGIN_OPERATIONS_PARTIALLY_FAILED = "WaitingForPluginOperationsPartiallyFailed"
    COMPLETED = "Completed"
    PARTIALLY_FAILED = "PartiallyFailed"
    FAILED = "Failed"


# UPLOADER
class UploaderConfig(BaseModel):
    writeSparseFiles: Optional[bool] = True
    parallelFilesDownload: Optional[int] = 10


# RESTORE SPEC
class RestoreSpec(BaseModel):
    backupName: Optional[str] = None
    scheduleName: Optional[str] = None
    itemOperationTimeout: Optional[str] = "4h"
    uploaderConfig: Optional[UploaderConfig] = None
    includedNamespaces: Optional[List[str]] = None
    excludedNamespaces: Optional[List[str]] = None
    includedResources: Optional[List[str]] = None
    excludedResources: Optional[List[str]] = None
    restoreStatus: Optional[Dict[str, List[str]]] = None
    includeClusterResources: Optional[bool] = None
    labelSelector: Optional[Dict[str, Dict[str, str]]] = None
    orLabelSelectors: Optional[List[Dict[str, Dict[str, str]]]] = None
    namespaceMapping: Optional[Dict[str, str]] = None
    restorePVs: Optional[bool] = None
    preserveNodePorts: Optional[bool] = None
    existingResourcePolicy: Optional[str] = None
    resourceModifier: Optional[Dict[str, str]] = None
    hooks: Optional[Dict[str, List[Dict[str, str]]]] = None


# RESTORE STATUS
class RestoreStatusDetails(BaseModel):
    phase: Optional[Literal[
        "New", "FailedValidation", "InProgress", "WaitingForPluginOperations",
        "WaitingForPluginOperationsPartiallyFailed", "Completed", "PartiallyFailed", "Failed"
    ]] = None
    validationErrors: Optional[List[str]] = None
    restoreItemOperationsAttempted: Optional[int] = 0
    restoreItemOperationsCompleted: Optional[int] = 0
    restoreItemOperationsFailed: Optional[int] = 0
    warnings: Optional[int] = 0
    errors: Optional[int] = 0
    failureReason: Optional[str] = None

    class Config:
        extra = "allow"

    # RESTORE METADATA
class RestoreMetadata(BaseModel):
    name: str
    namespace: str
    uid: Optional[str] = None  # for read
    resourceVersion: Optional[str] = None  # for read
    generation: Optional[int] = None  # for read
    creationTimestamp: Optional[str] = None  # for read
    labels: Optional[Dict[str, str]] = None  # for read
    annotations: Optional[Dict[str, str]] = None  # for read
    managedFields: Optional[List[Dict[str, Any]]] = None  # for read

    class Config:
        extra = "allow"

# RESTORE RESPONSE
class RestoreResponseSchema(BaseModel):
    apiVersion: str = "velero.io/v1"
    kind: str = "Restore"
    metadata: RestoreMetadata
    spec: Optional[RestoreSpec] = None
    status: Optional[RestoreStatusDetails] = None

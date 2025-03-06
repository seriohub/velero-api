from pydantic import BaseModel
from typing import Optional, Dict, List
# from datetime import datetime


class BackupRepositoryMetadata(BaseModel):
    """Represents the metadata section of a BackupRepository."""
    name: str
    generateName: Optional[str]
    namespace: str
    uid: str
    resourceVersion: Optional[str]
    generation: Optional[int]
    creationTimestamp: Optional[str]
    labels: Optional[Dict[str, str]]
    managedFields: Optional[List[Dict]]

    class Config:
        extra = "allow"


class BackupRepositorySpec(BaseModel):
    """Represents the spec section of a BackupRepository."""
    volumeNamespace: Optional[str]
    backupStorageLocation: Optional[str]
    repositoryType: Optional[str]
    resticIdentifier: Optional[str]
    maintenanceFrequency: Optional[str]

    class Config:
        extra = "allow"


class BackupRepositoryStatus(BaseModel):
    """Represents the status section of a BackupRepository."""
    phase: Optional[str] = None
    message: Optional[str] = None
    lastMaintenanceTime: Optional[str] = None

    class Config:
        extra = "allow"


class BackupRepositoryResponseSchema(BaseModel):
    """Full response schema for a BackupRepository object."""
    kind: str
    apiVersion: str
    metadata: BackupRepositoryMetadata
    spec: Optional[BackupRepositorySpec] = None
    status: Optional[BackupRepositoryStatus] = None

    class Config:
        extra = "allow"

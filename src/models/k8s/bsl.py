from pydantic import BaseModel, Field
from typing import Optional, Dict


class BSLObjectStorage(BaseModel):
    """Definisce la configurazione per l'Object Storage"""
    bucket: str
    prefix: Optional[str] = None
    caCert: Optional[str] = None

    class Config:
        extra = "allow"

class BSLCredential(BaseModel):
    """Definisce le credenziali del provider di storage"""
    name: str
    key: str


class BackupStorageLocationSpec(BaseModel):
    """Definisce la configurazione dello Storage Location"""
    provider: str
    objectStorage: Optional[BSLObjectStorage] = None
    credential: Optional[BSLCredential] = None
    backupSyncPeriod: Optional[str] = "2m0s"
    validationFrequency: Optional[str] = None
    config: Optional[Dict[str, str]] = None

    class Config:
        extra = "allow"


class BackupStorageLocationMetadata(BaseModel):
    """Definisce i metadati dello Storage Location"""
    name: str
    namespace: Optional[str] = "velero"
    uid: Optional[str]

    class Config:
        extra = "allow"


class BackupStorageLocationStatus(BaseModel):
    """Definisce lo stato dello Storage Location"""
    phase: Optional[str] = None
    lastSyncedTime: Optional[str] = None
    errors: Optional[int] = 0


class BackupStorageLocationResponseSchema(BaseModel):
    """Schema completo per un Backup Storage Location"""
    apiVersion: str = "velero.io/v1"
    kind: str = "BackupStorageLocation"
    metadata: BackupStorageLocationMetadata
    spec: BackupStorageLocationSpec
    status: Optional[BackupStorageLocationStatus] = None

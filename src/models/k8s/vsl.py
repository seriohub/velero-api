from pydantic import BaseModel, Field
from typing import Optional, Dict


class VolumeSnapshotLocationMetadataResponse(BaseModel):
    """Response metadata for VolumeSnapshotLocation"""
    name: str
    namespace: Optional[str]
    uid: Optional[str] = None
    resourceVersion: Optional[str] = None
    creationTimestamp: Optional[str] = None
    labels: Optional[Dict[str, str]] = None
    annotations: Optional[Dict[str, str]] = None

    class Config:
        extra = "allow"


class VolumeSnapshotLocationSpecResponse(BaseModel):
    """Response specification for VolumeSnapshotLocation"""
    provider: str
    credentialName: Optional[str] = None
    credentialKey: Optional[str] = None
    config: Optional[Dict[str, str]] = None

    class Config:
        extra = "allow"


class VolumeSnapshotLocationResponseSchema(BaseModel):
    """Full response schema for VolumeSnapshotLocation"""
    apiVersion: str
    kind: str

    metadata: Optional[VolumeSnapshotLocationMetadataResponse]
    spec: Optional[VolumeSnapshotLocationSpecResponse]

    class Config:
        extra = "allow"

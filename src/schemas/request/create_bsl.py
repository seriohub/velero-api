from pydantic import BaseModel, Field
from typing import Optional, Dict
from configs.config_boot import config_app


class CreateBslRequestSchema(BaseModel):
    name: str = Field(..., description="The name of the BSL.")
    namespace: Optional[str] = config_app.k8s.velero_namespace

    provider: str = Field(..., description="The name of the provider.")
    bucket: str = Field(..., description="The S3 bucket name.")
    prefix: str = Field(..., description="The S3 prefix name.")
    accessMode: str = Field(..., description="The access mode (e.g., read, write).")

    config:  Optional[Dict[str, str]] = Field(None, description="Configuration fields.")

    credentialName: str = Field(..., description="The name of the existing secret containing credentials.")
    credentialKey: str = Field(..., description="The key within the secret for the credentials.")

    backupSyncPeriod: str = Field("2m0s", description="The synchronization period (e.g., '15m', '1h').")
    validationFrequency: str = Field("1m", description="The validation frequency (e.g., '1h', '24h').")

    default: bool = Field(False, description="Whether this BSL is the default.")

from pydantic import BaseModel, Field
from typing import Optional, Dict
from vui_common.configs.config_proxy import config_app


class UpdateVslRequestSchema(BaseModel):
    name: str = Field(..., description="The name of the VSL.")
    namespace: Optional[str] = config_app.k8s.velero_namespace
    provider: str = Field(..., description="The name of the provider.")

    config: Optional[Dict[str, str]] = Field(None, description="Configuration fields.")

    credentialName: Optional[str] = Field(None, description="The name of the existing secret containing credentials.")
    credentialKey: Optional[str] = Field(None, description="The key within the secret for the credentials.")

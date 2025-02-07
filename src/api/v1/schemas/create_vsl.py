from pydantic import BaseModel, Field
from typing import Optional


class CreateVsl(BaseModel):
    name: str = Field(..., description="The name of the BSL.")
    provider: str = Field(..., description="The name of the provider.")

    config: Optional[list] = Field(None, description="Configuration fields.")

    credentialSecretName: str = Field(..., description="The name of the existing secret containing credentials.")
    credentialKey: str = Field(..., description="The key within the secret for the credentials.")

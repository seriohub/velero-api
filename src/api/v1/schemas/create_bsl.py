from pydantic import BaseModel, Field
from typing import Optional


class CreateBsl(BaseModel):
    name: str = Field(..., description="The name of the BSL.")
    provider: str = Field(..., description="The name of the provider.")
    bucketName: str = Field(..., description="The S3 bucket name.")
    accessMode: str = Field(..., description="The access mode (e.g., read, write).")

    # region: str = Field(..., description="The AWS region of the bucket.")
    # s3Url: Optional[Union[HttpUrl, str]] = Field(None, description="The S3 bucket URL.")
    config: Optional[list] = Field(None, description="Configuration fields.")

    credentialSecretName: str = Field(..., description="The name of the existing secret containing credentials.")
    credentialKey: str = Field(..., description="The key within the secret for the credentials.")

    newSecretName: Optional[str] = Field(None, description="The name of a new secret to create.")
    newSecretKey: Optional[str] = Field(None, description="The key for the new secret.")
    awsAccessKeyId: Optional[str] = Field(None, description="The AWS Access Key ID.")
    awsSecretAccessKey: Optional[str] = Field(None, description="The AWS Secret Access Key.")

    synchronizationPeriod: str = Field(..., description="The synchronization period (e.g., '15m', '1h').")
    validationFrequency: str = Field(..., description="The validation frequency (e.g., '1h', '24h').")

    default: bool = Field(False, description="Whether this BSL is the default.")

    # @field_validator("s3Url", mode="before")
    # def allow_empty_string(cls, value):
    #     if value == "":
    #         return None
    #     return value
    # class Config:
    #     schema_extra = {
    #         "example": {
    #             "name": "example-bsl",
    #             "provider": "aws",
    #             "bucketName": "example-bucket",
    #             "accessMode": "read",
    #             "region": "us-east-1",
    #             "s3Url": "https://s3.us-east-1.amazonaws.com/example-bucket",
    #             "credentialSecretName": "my-credentials",
    #             "credentialKey": "access-key",
    #             "newSecretName": "new-credentials",
    #             "newSecretKey": "new-key",
    #             "awsAccessKeyId": "AKIAEXAMPLE",
    #             "awsSecretAccessKey": "EXAMPLESECRETKEY",
    #             "synchronizationPeriod": "1h",
    #             "validationFrequency": "24h",
    #             "default": False
    #         }
    #     }

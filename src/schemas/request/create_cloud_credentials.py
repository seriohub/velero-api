from pydantic import BaseModel


class CreateCloudCredentialsRequestSchema(BaseModel):
    newSecretName: str
    newSecretKey: str
    awsAccessKeyId: str
    awsSecretAccessKey: str

from pydantic import BaseModel


class CreateCloudCredentials(BaseModel):
    newSecretName: str
    newSecretKey: str
    awsAccessKeyId: str
    awsSecretAccessKey: str

from pydantic import BaseModel


class StorageClassMapRequestSchema(BaseModel):
    storageClassMapping: dict

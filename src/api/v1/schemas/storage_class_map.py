from pydantic import BaseModel


class StorageClassMap(BaseModel):
    storageClassMapping: dict

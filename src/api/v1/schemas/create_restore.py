from pydantic import BaseModel


class CreateRestore(BaseModel):
    resourceType: str
    resourceName: str
    mappingNamespaces: list = []
    parameters: str = ''

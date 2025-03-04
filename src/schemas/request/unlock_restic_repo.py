from pydantic import BaseModel


class UnlockResticRepoRequestSchema(BaseModel):
    bsl: str
    repositoryUrl: str
    removeAll: bool

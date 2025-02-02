from pydantic import BaseModel


class UnlockResticRepo(BaseModel):
    bsl: str
    repositoryUrl: str
    removeAll: bool

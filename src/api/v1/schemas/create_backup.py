from pydantic import BaseModel
class CreateBackup(BaseModel):
    name: str
    includedNamespaces: list
    excludedNamespaces: list
    includedResources: list
    excludedResources: list
    backupRetention: str
    snapshotVolumes: bool
    includeClusterResources: bool
    defaultVolumesToFsBackup: bool
    backupLabel: str
    selector: str
    backupLocation: str
    snapshotLocation: list



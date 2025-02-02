from pydantic import BaseModel


class UpdateSchedule(BaseModel):
    name: str
    oldName: str
    includedNamespaces: list = []
    excludedNamespaces: list = []
    includedResources: list = []
    excludedResources: list = []
    backupRetention: str
    snapshotVolumes: bool = False
    includeClusterResources: str = ''
    defaultVolumesToFsBackup: bool = False
    backupLabel: str = ''
    selector: str = ''
    backupLocation: str = ''
    snapshotLocation: list = []
    schedule: str

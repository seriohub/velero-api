from pydantic import BaseModel


class UpdateScheduleRequestSchema(BaseModel):
    name: str

    # spec
    schedule: str

    # spec.template
    includedNamespaces: list
    excludedNamespaces: list
    includedResources: list
    excludedResources: list
    ttl: str
    snapshotVolumes: bool
    includeClusterResources: bool
    defaultVolumesToFsBackup: bool
    storageLocation: str
    volumeSnapshotLocations: list

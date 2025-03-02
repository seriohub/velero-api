from dataclasses import dataclass
from enum import Enum
from typing import Dict


@dataclass(frozen=True)
class Resource:
    name: str
    kind: str
    plural: str


class ResourcesNames(Enum):
    BACKUP = "BACKUP"
    RESTORE = "RESTORE"
    SCHEDULE = "SCHEDULE"
    DOWNLOAD_REQUEST = "DOWNLOAD_REQUEST"
    DELETE_BACKUP_REQUEST = "DELETE_BACKUP_REQUEST"
    POD_VOLUME_BACKUP = "POD_VOLUME_BACKUP"
    POD_VOLUME_RESTORE = "POD_VOLUME_RESTORE"
    BACKUP_REPOSITORY = "BACKUP_REPOSITORY"
    RESTIC_REPOSITORY = "RESTIC_REPOSITORY"
    BACKUP_STORAGE_LOCATION = "BACKUP_STORAGE_LOCATION"
    VOLUME_SNAPSHOT_LOCATION = "VOLUME_SNAPSHOT_LOCATION"
    SERVER_STATUS_REQUEST = "SERVER_STATUS_REQUEST"


PLURALS = [
    "backups",
    "restores",
    "schedules",
    "downloadrequests",
    "deletebackuprequests",
    "podvolumebackups",
    "podvolumerestores",
    "resticrepositories",
    "backuprepositories",
    "backupstoragelocations",
    "volumesnapshotlocations",
    "serverstatusrequests",
]

RESOURCES: Dict[ResourcesNames, Resource] = {
    ResourcesNames.BACKUP: Resource("Backup", "Backup", "backups"),
    ResourcesNames.RESTORE: Resource("Restore", "Restore", "restores"),
    ResourcesNames.SCHEDULE: Resource("Schedule", "Schedule", "schedules"),
    ResourcesNames.DOWNLOAD_REQUEST: Resource("Download Request", "DownloadRequest", "downloadrequests"),
    ResourcesNames.DELETE_BACKUP_REQUEST: Resource("Delete Backup Request", "DeleteBackupRequest","deletebackuprequests"),
    ResourcesNames.POD_VOLUME_BACKUP: Resource("Pod Volume Backup", "PodVolumeBackup", "podvolumebackups"),
    ResourcesNames.POD_VOLUME_RESTORE: Resource("Pod Volume Restore", "PodVolumeRestore", "podvolumerestores"),
    ResourcesNames.RESTIC_REPOSITORY: Resource("Restic Repository", "ResticRepository", "resticrepositories"),
    ResourcesNames.BACKUP_REPOSITORY: Resource("Backup Repository", "BackupRepository", "backuprepositories"),
    ResourcesNames.BACKUP_STORAGE_LOCATION: Resource("Backup Storage Location", "BackupStorageLocation","backupstoragelocations"),
    ResourcesNames.VOLUME_SNAPSHOT_LOCATION: Resource("Volume Snapshot Location", "VolumeSnapshotLocation","volumesnapshotlocations"),
    ResourcesNames.SERVER_STATUS_REQUEST: Resource("Server Status Request", "ServerStatusRequest","serverstatusrequests"),
}

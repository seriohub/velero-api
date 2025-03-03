from typing import List

from datetime import datetime

from fastapi import HTTPException
from kubernetes import client

from service.utils.download_request import create_download_request
from utils.k8s_tracer import trace_k8s_async_method

from configs.config_boot import config_app

from constants.velero import VELERO
from constants.resources import RESOURCES, ResourcesNames

from schemas.request.create_backup import CreateBackupRequestSchema

from models.k8s.backup import BackupResponseSchema

custom_objects = client.CustomObjectsApi()


# @trace_k8s_async_method(description="Get backups list")
async def get_backups_service(schedule_name: str | None = None, latest_per_schedule: bool = False,
                              in_progress: bool = False) -> List[BackupResponseSchema]:
    """Retrieve all Velero backups"""
    backups = custom_objects.list_namespaced_custom_object(
        group=VELERO["GROUP"],
        version=VELERO["VERSION"],
        namespace=config_app.k8s.velero_namespace,
        plural=RESOURCES[ResourcesNames.BACKUP].plural
    )

    filtered_backups = {}
    now = datetime.utcnow()

    for item in backups.get("items", []):
        metadata = item["metadata"]
        labels = metadata.get("labels", {})
        backup_schedule_name = labels.get("velero.io/schedule-name")
        creation_timestamp = metadata.get("creationTimestamp")
        status = item.get("status", {})
        phase = status.get("phase", "").lower()
        completion_timestamp = status.get("completionTimestamp")

        # If a `schedule_name` filter is specified, it skips backups that do not match
        if schedule_name and backup_schedule_name != schedule_name:
            continue

        if in_progress:
            has_completion_timestamp = completion_timestamp is not None
            diff_in_seconds = None

            if has_completion_timestamp:
                datetime_completion_timestamp = datetime.strptime(completion_timestamp, '%Y-%m-%dT%H:%M:%SZ')
                diff_in_seconds = (now - datetime_completion_timestamp).total_seconds()

            if not (
                    phase.endswith("ing") or
                    phase == "inprogress" or
                    (has_completion_timestamp and diff_in_seconds is not None and diff_in_seconds < 180)
            ):
                continue

        # If `latest_per_schedule` is enabled, it saves only the last backup for each schedule
        if latest_per_schedule and backup_schedule_name:
            if backup_schedule_name in filtered_backups:
                existing_timestamp = filtered_backups[backup_schedule_name]["metadata"]["creationTimestamp"]
                if creation_timestamp > existing_timestamp:
                    filtered_backups[backup_schedule_name] = item
            else:
                filtered_backups[backup_schedule_name] = item
        else:
            # If `latest_per_schedule` is disabled, add all backups
            filtered_backups[metadata["uid"]] = item

    # Let's build the backup list
    backup_list = [BackupResponseSchema(**item) for item in filtered_backups.values()]
    return backup_list


@trace_k8s_async_method(description="Get backup details")
async def get_backup_details_service(backup_name: str) -> BackupResponseSchema:
    """Retrieve details of a single backup"""

    backup = custom_objects.get_namespaced_custom_object(
        group=VELERO["GROUP"],
        version=VELERO["VERSION"],
        namespace=config_app.k8s.velero_namespace,
        plural=RESOURCES[ResourcesNames.BACKUP].plural,
        name=backup_name
    )

    return BackupResponseSchema(**backup)


@trace_k8s_async_method(description="Delete backup")
async def delete_backup_service(backup_name: str):
    """Delete a Velero backup"""
    response = custom_objects.delete_namespaced_custom_object(
        group=VELERO["GROUP"],
        version=VELERO["VERSION"],
        namespace=config_app.k8s.velero_namespace,
        plural=RESOURCES[ResourcesNames.BACKUP].plural,
        name=backup_name
    )
    return response


@trace_k8s_async_method(description="Create backup")
async def create_backup_service(backup_data: CreateBackupRequestSchema):
    """Create a Velero backup on Kubernetes"""
    spec = backup_data.model_dump(exclude_unset=True)
    spec.pop("name", None)
    spec.pop("namespace", None)
    spec.pop("labelSelector", None)
    spec.pop("orLabelSelectors", None)
    spec.pop("parallelFilesUpload", None)

    backup_body = {
        "apiVersion": f"{VELERO['GROUP']}/{VELERO['VERSION']}",
        "kind": RESOURCES[ResourcesNames.BACKUP].name,
        "metadata": {
            "name": backup_data.name,
            "namespace": backup_data.namespace
        },
        "spec": spec
    }

    if backup_data.labelSelector:
        backup_body['spec']["labelSelector"] = {'matchLabels': backup_data.labelSelector}

    if backup_data.parallelFilesUpload:
        backup_body['spec']['uploaderConfig'] = {}
        backup_body['spec']['uploaderConfig']["parallelFilesUpload"] = backup_data.parallelFilesUpload

    response = custom_objects.create_namespaced_custom_object(
        group=VELERO["GROUP"],
        version=VELERO["VERSION"],
        namespace=backup_data.namespace,
        plural=RESOURCES[ResourcesNames.BACKUP].plural,
        body=backup_body
    )

    return response


@trace_k8s_async_method(description="Create backup from schedule name")
async def create_backup_from_schedule_service(schedule_name: str):
    """Create a backup based on a Velero schedule"""
    namespace = config_app.k8s.velero_namespace

    #  Generate a name for the backup
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    backup_name = f"{schedule_name}-{timestamp}"

    # Defining the payload for creating the backup
    backup_body = {
        "apiVersion": f"{VELERO['GROUP']}/{VELERO['VERSION']}",
        "kind": RESOURCES[ResourcesNames.BACKUP].name,
        "metadata": {
            "name": backup_name,
            "namespace": namespace,
            "labels": {
                "velero.io/schedule-name": schedule_name
            }
        }
    }

    response = custom_objects.create_namespaced_custom_object(
        group=VELERO["GROUP"],
        version=VELERO["VERSION"],
        namespace=namespace,
        plural=RESOURCES[ResourcesNames.BACKUP].plural,
        body=backup_body
    )

    return response


@trace_k8s_async_method(description="Update backup expiration")
async def update_backup_expiration_service(backup_name: str, expiration: str):
    # get backup object
    backup = custom_objects.get_namespaced_custom_object(
        group=VELERO["GROUP"],
        version=VELERO["VERSION"],
        namespace=config_app.k8s.velero_namespace,
        plural=RESOURCES[ResourcesNames.BACKUP].plural,
        name=backup_name)

    # edit ttl
    backup['status']['expiration'] = expiration

    # update ttl field
    response = custom_objects.replace_namespaced_custom_object(
        group=VELERO["GROUP"],
        version=VELERO["VERSION"],
        namespace=config_app.k8s.velero_namespace,
        plural=RESOURCES[ResourcesNames.BACKUP].plural, name=backup_name,
        body=backup)

    return response


@trace_k8s_async_method(description="Get backup expiration")
async def get_backup_expiration_service(backup_name: str):
    backup = await get_backup_details_service(backup_name)

    return backup.status.expiration


@trace_k8s_async_method(description="Download backup")
async def download_backup_service(backup_name: str) -> dict:
    # Create a DownloadRequest to retrieve backup data
    download_url = await create_download_request(backup_name, "BackupContents")
    if not download_url:
        raise HTTPException(status_code=400, detail=f"Create a DownloadRequest to retrieve backup data")
    return {'url': download_url}

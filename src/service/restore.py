from typing import List

from kubernetes import client, config

from utils.k8s_tracer import trace_k8s_async_method
from configs.velero import VELERO
from configs.resources import RESOURCES, ResourcesNames
from datetime import datetime
from schemas.request.create_restore import CreateRestoreRequestSchema
from models.k8s.restore import RestoreResponseSchema
from configs.config_boot import config_app



custom_objects = client.CustomObjectsApi()



# @trace_k8s_async_method(description="get a restores list")
async def get_restores_service(in_progress: bool = False) -> List[RestoreResponseSchema]:
    """Retrieve all Velero schedules"""

    restores = custom_objects.list_namespaced_custom_object(
        group=VELERO["GROUP"],
        version=VELERO["VERSION"],
        namespace=config_app.get_k8s_velero_namespace(),
        plural=RESOURCES[ResourcesNames.RESTORE].plural
    )

    filtered_restores = {}
    now = datetime.utcnow()

    for item in restores.get("items", []):
        metadata = item["metadata"]
        status = item.get("status", {})
        phase = status.get("phase", "").lower()
        completion_timestamp = status.get("completionTimestamp")

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

        filtered_restores[metadata["uid"]] = item

    restore_list = [RestoreResponseSchema(**item) for item in filtered_restores.values()]

    return restore_list


@trace_k8s_async_method(description="get a restore details")
async def get_restore_details_service(restore_name: str) -> RestoreResponseSchema:
    """Retrieve details of a single schedule"""
    restore = custom_objects.get_namespaced_custom_object(
        group=VELERO["GROUP"],
        version=VELERO["VERSION"],
        namespace=config_app.get_k8s_velero_namespace(),
        plural=RESOURCES[ResourcesNames.RESTORE].plural,
        name=restore_name
    )
    return RestoreResponseSchema(**restore)


@trace_k8s_async_method(description="create a restore")
async def create_restore_service(restore_data: CreateRestoreRequestSchema):
    """Create a Velero restore on Kubernetes"""
    backup_dict = restore_data.model_dump(exclude_unset=True)
    backup_dict.pop("name", None)
    backup_dict.pop("namespace", None)

    restore_body = {
        "apiVersion": f"{VELERO['GROUP']}/{VELERO['VERSION']}",
        "kind": RESOURCES[ResourcesNames.RESTORE].name,
        "metadata": {"name": restore_data.name, "namespace": restore_data.namespace},
        "spec": restore_data.model_dump(exclude_unset=True)
    }

    response = custom_objects.create_namespaced_custom_object(
        group=VELERO["GROUP"],
        version=VELERO["VERSION"],
        namespace=restore_data.namespace,
        plural=RESOURCES[ResourcesNames.RESTORE].plural,
        body=restore_body
    )

    return response

@trace_k8s_async_method(description="delete a restore")
async def delete_restore_service(restore_name: str):
    """
    Delete an existing Restore from Kubernetes.
    """

    response = custom_objects.delete_namespaced_custom_object(
        group=VELERO["GROUP"],
        version=VELERO["VERSION"],
        namespace=config_app.get_k8s_velero_namespace(),
        plural=RESOURCES[ResourcesNames.RESTORE].plural,
        name=restore_name
    )
    return response

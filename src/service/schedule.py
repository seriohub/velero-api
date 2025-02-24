from typing import List

from kubernetes import client

from models.k8s.schedule import ScheduleResponseSchema
from schemas.request.create_schedule import CreateScheduleRequestSchema

from configs.config_boot import config_app
from constants.velero import VELERO
from constants.resources import RESOURCES, ResourcesNames
from utils.k8s_tracer import trace_k8s_async_method

custom_objects = client.CustomObjectsApi()


@trace_k8s_async_method(description="Get velero schedules")
async def get_schedules_service() -> List[ScheduleResponseSchema]:
    schedules = custom_objects.list_namespaced_custom_object(
        group=VELERO["GROUP"],
        version=VELERO["VERSION"],
        namespace=config_app.k8s.velero_namespace,
        plural=RESOURCES[ResourcesNames.SCHEDULE].plural
    )

    schedule_list = [ScheduleResponseSchema(**item) for item in schedules.get("items", [])]
    return schedule_list


@trace_k8s_async_method(description="Set pause schedule")
async def pause_schedule_service(schedule_name, paused=True):
    schedule = custom_objects.get_namespaced_custom_object(
        group=VELERO["GROUP"],
        version=VELERO["VERSION"],
        namespace=config_app.k8s.velero_namespace,
        plural=RESOURCES[ResourcesNames.SCHEDULE].plural,
        name=schedule_name
    )

    schedule["spec"]["paused"] = paused

    response = custom_objects.replace_namespaced_custom_object(
        group=VELERO["GROUP"],
        version=VELERO["VERSION"],
        namespace=config_app.k8s.velero_namespace,
        plural=RESOURCES[ResourcesNames.SCHEDULE].plural,
        name=schedule_name,
        body=schedule
    )

    return response


@trace_k8s_async_method(description="Create schedule")
async def create_schedule_service(schedule: CreateScheduleRequestSchema):
    """Create a Velero schedule on Kubernetes"""
    schedule_dict = schedule.model_dump(exclude_unset=True)
    schedule_dict.pop("name", None)
    schedule_dict.pop("namespace", None)

    schedule_body = {
        "apiVersion": f"{VELERO['GROUP']}/{VELERO['VERSION']}",
        "kind": RESOURCES[ResourcesNames.SCHEDULE].name,
        "metadata": {
            "name": schedule.name,
            "namespace": schedule.namespace
        },
        "spec": schedule_dict
    }

    response = custom_objects.create_namespaced_custom_object(
        group=VELERO["GROUP"],
        version=VELERO["VERSION"],
        namespace=config_app.k8s.velero_namespace,
        plural=RESOURCES[ResourcesNames.SCHEDULE].plural,
        body=schedule_body
    )

    return response


@trace_k8s_async_method(description="Delete schedule")
async def delete_schedule_service(schedule_name: str):
    """Delete a Velero schedule"""
    response = custom_objects.delete_namespaced_custom_object(
        group=VELERO["GROUP"],
        version=VELERO["VERSION"],
        namespace=config_app.k8s.velero_namespace,
        plural=RESOURCES[ResourcesNames.SCHEDULE].plural,
        name=schedule_name
    )
    return response


@trace_k8s_async_method(description="Update schedule")
async def update_schedule_service(schedule_data):
    existing_schedule = custom_objects.get_namespaced_custom_object(
        group=VELERO["GROUP"],
        version=VELERO["VERSION"],
        namespace=config_app.k8s.velero_namespace,
        plural=RESOURCES[ResourcesNames.SCHEDULE].plural,
        name=schedule_data.name
    )

    # Update the necessary fields
    existing_schedule["spec"]["schedule"] = schedule_data.schedule
    existing_schedule["spec"]["template"]["includedNamespaces"] = schedule_data.includedNamespaces
    existing_schedule["spec"]["template"]["excludedNamespaces"] = schedule_data.excludedNamespaces
    existing_schedule["spec"]["template"]["includedResources"] = schedule_data.includedResources
    existing_schedule["spec"]["template"]["excludedResources"] = schedule_data.excludedResources
    existing_schedule["spec"]["template"]["ttl"] = schedule_data.ttl
    existing_schedule["spec"]["template"]["snapshotVolumes"] = schedule_data.snapshotVolumes
    existing_schedule["spec"]["template"]["includeClusterResources"] = schedule_data.includeClusterResources
    existing_schedule["spec"]["template"]["defaultVolumesToFsBackup"] = schedule_data.defaultVolumesToFsBackup
    existing_schedule["spec"]["template"]["storageLocation"] = schedule_data.storageLocation
    existing_schedule["spec"]["template"]["volumeSnapshotLocations"] = schedule_data.volumeSnapshotLocations

    #  Update the Schedule with the new settings
    response = custom_objects.replace_namespaced_custom_object(
        group=VELERO["GROUP"],
        version=VELERO["VERSION"],
        namespace=config_app.k8s.velero_namespace,
        plural=RESOURCES[ResourcesNames.SCHEDULE].plural,
        name=schedule_data.name,
        body=existing_schedule
    )
    return response

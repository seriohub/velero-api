from typing import List

from kubernetes import client

from models.k8s.schedule import ScheduleResponseSchema
from schemas.request.create_schedule import CreateScheduleRequestSchema

from vui_common.configs.config_proxy import config_app
from constants.velero import VELERO
from constants.resources import RESOURCES, ResourcesNames
from vui_common.utils.k8s_tracer import trace_k8s_async_method

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
async def create_schedule_service(schedule_data: CreateScheduleRequestSchema):
    """Create a Velero schedule on Kubernetes"""
    template = schedule_data.model_dump(exclude_unset=True)
    template.pop("name", None)
    template.pop("namespace", None)
    template.pop("schedule", None)
    template.pop("paused", None)
    template.pop("useOwnerReferencesInBackup", None)
    template.pop("labelSelector", None)
    template.pop("orLabelSelectors", None)
    template.pop("parallelFilesUpload", None)
    template.pop("resourcePolicy", None)

    schedule_body = {
        "apiVersion": f"{VELERO['GROUP']}/{VELERO['VERSION']}",
        "kind": RESOURCES[ResourcesNames.SCHEDULE].name,
        "metadata": {
            "name": schedule_data.name,
            "namespace": schedule_data.namespace
        },
        "spec": {
            "schedule": schedule_data.schedule,
            "paused": schedule_data.paused,
            "useOwnerReferencesInBackup": schedule_data.useOwnerReferencesInBackup,
            "template": template
        },
    }

    if schedule_data.labelSelector:
        schedule_body['spec']['template']["labelSelector"] = {'matchLabels': schedule_data.labelSelector}

    if schedule_data.parallelFilesUpload:
        schedule_body['spec']['template']['uploaderConfig'] = {}
        schedule_body['spec']['template']['uploaderConfig']["parallelFilesUpload"] = schedule_data.parallelFilesUpload

    if schedule_data.resourcePolicy:
        schedule_body['spec']['template']["resourcePolicy"] = {'kind': 'configmap', 'name': schedule_data.resourcePolicy}

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
    existing_schedule["spec"]["paused"] = schedule_data.paused
    existing_schedule["spec"]["useOwnerReferencesInBackup"] = schedule_data.useOwnerReferencesInBackup

    template = schedule_data.model_dump(exclude_unset=True)
    template.pop("name", None)
    template.pop("namespace", None)
    template.pop("schedule", None)
    template.pop("paused", None)
    template.pop("useOwnerReferencesInBackup", None)
    template.pop("labelSelector", None)
    template.pop("orLabelSelectors", None)
    template.pop("parallelFilesUpload", None)

    new_spec = {
        "schedule": schedule_data.schedule,
        "paused": schedule_data.paused,
        "useOwnerReferencesInBackup": schedule_data.useOwnerReferencesInBackup,
        "template": template
    }

    if schedule_data.labelSelector:
        # config_dict = {list(item.keys())[0]: list(item.values())[0] for item in schedule_data.labelSelector}
        new_spec['template']["labelSelector"] = {'matchLabels': schedule_data.labelSelector}

    if schedule_data.parallelFilesUpload:
        new_spec['template']['uploaderConfig'] = {}
        new_spec['template']['uploaderConfig']["parallelFilesUpload"] = schedule_data.parallelFilesUpload

    existing_schedule['spec'] = new_spec

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

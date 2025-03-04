from models.k8s.vsl import VolumeSnapshotLocationResponseSchema
from schemas.request.create_vsl import CreateVslRequestSchema

from kubernetes import client

from utils.k8s_tracer import trace_k8s_async_method

from configs.config_boot import config_app
from constants.velero import VELERO
from constants.resources import RESOURCES, ResourcesNames

custom_objects = client.CustomObjectsApi()


@trace_k8s_async_method(description="Get Volume Snapshot Locations")
async def get_vsls_service():
    vsl = custom_objects.list_namespaced_custom_object(
        group=VELERO["GROUP"],
        version=VELERO["VERSION"],
        namespace=config_app.k8s.velero_namespace,
        plural=RESOURCES[ResourcesNames.VOLUME_SNAPSHOT_LOCATION].plural,
    )
    vsl_list = [VolumeSnapshotLocationResponseSchema(**item) for item in vsl.get("items", [])]
    return vsl_list


@trace_k8s_async_method(description="Create Volume Snapshot Locations")
async def create_vsl_service(vsl_data: CreateVslRequestSchema):
    """
    Create a new VolumeSnapshotLocation in Kubernetes via the Velero API.
    """
    vsl_body = {
        "apiVersion": "velero.io/v1",
        "kind": "VolumeSnapshotLocation",
        "metadata": {
            "name": vsl_data.name,
            "namespace": vsl_data.namespace
        },
        "spec": {
            "provider": vsl_data.provider
        }
    }

    if hasattr(vsl_data, "config") and len(vsl_data.config) > 0:
        vsl_body["spec"]["config"] = vsl_data.config

    if (hasattr(vsl_data, "credentialName") and
            hasattr(vsl_data, "credentialKey") and
            vsl_data.credentialName != ''
            and vsl_data.credentialKey != ''):
        vsl_body['spec']["credential"] = {
            "name": vsl_data.credentialName,
            "key": vsl_data.credentialKey
        }

    response = custom_objects.create_namespaced_custom_object(
        group=VELERO["GROUP"],
        version=VELERO["VERSION"],
        namespace=config_app.k8s.velero_namespace,
        plural=RESOURCES[ResourcesNames.VOLUME_SNAPSHOT_LOCATION].plural,
        body=vsl_body
    )
    return response


@trace_k8s_async_method(description="Delete Volume Snapshot Locations")
async def delete_vsl_service(vsl_name: str):
    """Delete a Velero BSL"""
    response = custom_objects.delete_namespaced_custom_object(
        group=VELERO["GROUP"],
        version=VELERO["VERSION"],
        namespace=config_app.k8s.velero_namespace,
        plural=RESOURCES[ResourcesNames.VOLUME_SNAPSHOT_LOCATION].plural,
        name=vsl_name
    )
    return response

from models.k8s.vsl import VolumeSnapshotLocationResponseSchema
from schemas.request.create_vsl import CreateVslRequestSchema

from kubernetes import client

from utils.logger_boot import logger

from configs.config_boot import config_app
from configs.velero import VELERO
from configs.resources import RESOURCES, ResourcesNames

custom_objects = client.CustomObjectsApi()


async def get_vsls_service():
    vsl = custom_objects.list_namespaced_custom_object(
        group=VELERO["GROUP"],
        version=VELERO["VERSION"],
        namespace=config_app.get_k8s_velero_namespace(),
        plural=RESOURCES[ResourcesNames.VOLUME_SNAPSHOT_LOCATION].plural,
    )
    print(vsl)
    vsl_list = [VolumeSnapshotLocationResponseSchema(**item) for item in vsl.get("items", [])]
    print(vsl_list)
    return vsl_list


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
            "provider": vsl_data.provider,
            "credential": {
                "name": vsl_data.credentialName,
                "key": vsl_data.credentialKey
            } if vsl_data.credentialName and vsl_data.credentialKey else None,
            "config": vsl_data.config or {}
        }
    }

    # Remove None values to avoid API errors
    vsl_body["spec"] = {k: v for k, v in vsl_body["spec"].items() if v is not None}

    response = custom_objects.create_namespaced_custom_object(
        group=VELERO["GROUP"],
        version=VELERO["VERSION"],
        namespace=config_app.get_k8s_velero_namespace(),
        plural=RESOURCES[ResourcesNames.VOLUME_SNAPSHOT_LOCATION].plural,
        body=vsl_body
    )
    return response


async def delete_vsl_service(vsl_name: str):
    """Delete a Velero BSL"""
    response = custom_objects.delete_namespaced_custom_object(
        group=VELERO["GROUP"],
        version=VELERO["VERSION"],
        namespace=config_app.get_k8s_velero_namespace(),
        plural=RESOURCES[ResourcesNames.VOLUME_SNAPSHOT_LOCATION].plural,
        name=vsl_name
    )
    return response

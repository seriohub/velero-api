from kubernetes import client

from vui_common.configs.config_proxy import config_app
from constants.velero import VELERO
from constants.resources import RESOURCES, ResourcesNames
from schemas.request.delete_resource import DeleteResourceRequestSchema
from service.utils.download_request import cleanup_download_request

custom_objects = client.CustomObjectsApi()


async def get_server_status_requests_service():
    ssr = custom_objects.list_namespaced_custom_object(
        group=VELERO["GROUP"],
        version=VELERO["VERSION"],
        namespace=config_app.k8s.velero_namespace,
        plural=RESOURCES[ResourcesNames.SERVER_STATUS_REQUEST].plural
    )

    return ssr


async def get_download_requests_service():
    dr = custom_objects.list_namespaced_custom_object(
        group=VELERO["GROUP"],
        version=VELERO["VERSION"],
        namespace=config_app.k8s.velero_namespace,
        plural=RESOURCES[ResourcesNames.DOWNLOAD_REQUEST].plural
    )

    return dr


async def get_delete_backup_requests_service():
    dbr = custom_objects.list_namespaced_custom_object(
        group=VELERO["GROUP"],
        version=VELERO["VERSION"],
        namespace=config_app.k8s.velero_namespace,
        plural=RESOURCES[ResourcesNames.DELETE_BACKUP_REQUEST].plural
    )

    return dbr

async def delete_download_requests_service(request: DeleteResourceRequestSchema):
    cleanup_download_request(request.name)

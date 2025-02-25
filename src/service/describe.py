from fastapi import HTTPException
from kubernetes import client
from schemas.velero_describe import VeleroDescribe
from constants.velero import VELERO
from constants.resources import RESOURCES, ResourcesNames
from configs.config_boot import config_app
from utils.k8s_tracer import trace_k8s_async_method

custom_objects = client.CustomObjectsApi()


@trace_k8s_async_method(description="Get velero resource details")
async def get_velero_resource_details_service(resource_name: str, resource_type: str) -> VeleroDescribe:
    """Gets the details of a Velero resource (Backup, Restore, etc.) directly from the Kubernetes API"""
    # if resource_type not in VELERO_RESOURCES:
    if resource_type.upper() not in ResourcesNames.__members__:
        # return VeleroDescribe(success=False, error=f"Unsupported resource type: {resource_type}")
        raise HTTPException(status_code=400, detail=f"Unsupported resource type: {resource_type}")

    try:
        resource_enum = ResourcesNames[resource_type.upper()]

        # Retrieve resource details directly from Kubernetes
        resource = custom_objects.get_namespaced_custom_object(
            group=VELERO['GROUP'],
            version=VELERO['VERSION'],
            namespace=config_app.k8s.velero_namespace,
            plural=RESOURCES[resource_enum].plural,
            name=resource_name
        )

        return VeleroDescribe(details=resource)

    except client.exceptions.ApiException as e:
        if e.status == 404:
            raise HTTPException(status_code=404, detail=f"{resource_type.capitalize()} '{resource_name}' not found.")
        raise HTTPException(status_code=400, detail=f"{str(e)}")

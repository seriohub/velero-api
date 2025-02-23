from models.k8s.bsl import BackupStorageLocationResponseSchema
from service.k8s import get_credential_service, get_default_credential_service

from schemas.request.create_bsl import CreateBslRequestSchema

from kubernetes import client

from utils.k8s_tracer import trace_k8s_async_method

from utils.logger_boot import logger

from configs.config_boot import config_app
from configs.velero import VELERO
from configs.resources import RESOURCES, ResourcesNames



custom_objects = client.CustomObjectsApi()


@trace_k8s_async_method(description="Gets bsls service")
async def get_bsls_service():
    bsls = custom_objects.list_namespaced_custom_object(
        group=VELERO["GROUP"],
        version=VELERO["VERSION"],
        namespace=config_app.get_k8s_velero_namespace(),
        plural=RESOURCES[ResourcesNames.BACKUP_STORAGE_LOCATION].plural
    )

    bsl_list = [BackupStorageLocationResponseSchema(**item) for item in bsls.get("items", [])]
    return bsl_list


@trace_k8s_async_method(description="Gets bsl details")
async def get_bsl_service(name: str):
    """
    Retrieve an existing Backup Storage Location.
    """

    bsl = custom_objects.get_namespaced_custom_object(
        group=VELERO["GROUP"],
        version=VELERO["VERSION"],
        namespace=config_app.get_k8s_velero_namespace(),
        plural=RESOURCES[ResourcesNames.BACKUP_STORAGE_LOCATION].plural,
        name=name
    )
    return bsl


@trace_k8s_async_method(description="Gets bsl credentials")
async def get_bsl_credentials_service(backup_storage_location: str):
    bsl = await get_bsl_service(backup_storage_location)

    if bsl.get('data') and isinstance(bsl, list) and len(bsl) > 0:
        credential_spec = bsl[0].get('spec', {}).get('credential')
    else:
        credential_spec = None
    if credential_spec:
        output = await get_credential_service(credential_spec['name'], credential_spec['key'])
    else:
        output = await get_default_credential_service()
    secret_name = output['aws_access_key_id']
    secret_key = output['aws_secret_access_key']
    return secret_name, secret_key


@trace_k8s_async_method(description="Create bsl")
async def create_bsl_service(bsl_data: CreateBslRequestSchema):
    """
    Create a Backup Storage Location (BSL) in Kubernetes using the Velero API..
    """

    # Creating the body of the request
    bsl_body = {
        "apiVersion": "velero.io/v1",
        "kind": "BackupStorageLocation",
        "metadata": {
            "name": bsl_data.name,
            "namespace": bsl_data.namespace,
        },
        "spec": {
            "provider": bsl_data.provider,
            "backupSyncPeriod": bsl_data.synchronizationPeriod,
            "validationFrequency": bsl_data.validationFrequency,
            "objectStorage": {
                "bucket": bsl_data.bucketName
            },
            "credential": {
                "name": bsl_data.credentialName,
                "key": bsl_data.credentialKey
            },
            "config": {field["key"]: field["value"] for field in bsl_data.config} if bsl_data.config else {}
        }
    }

    response = custom_objects.create_namespaced_custom_object(
        group=VELERO["GROUP"],
        version=VELERO["VERSION"],
        namespace=config_app.get_k8s_velero_namespace(),
        plural=RESOURCES[ResourcesNames.BACKUP_STORAGE_LOCATION].plural,
        body=bsl_body
    )

    return response


@trace_k8s_async_method(description="Delete bsl")
async def delete_bsl_service(bsl_name: str):
    """Delete a Velero BSL"""
    response = custom_objects.delete_namespaced_custom_object(
        group=VELERO["GROUP"],
        version=VELERO["VERSION"],
        namespace=config_app.get_k8s_velero_namespace(),
        plural=RESOURCES[ResourcesNames.BACKUP_STORAGE_LOCATION].plural,
        name=bsl_name
    )
    return response


@trace_k8s_async_method(description="Set default bsl")
async def set_default_bsl_service(bsl_name: str):
    # Recupera tutti i BSL esistenti per trovare quello attualmente predefinito
    bsl_list = custom_objects.list_namespaced_custom_object(
        group=VELERO["GROUP"],
        version=VELERO["VERSION"],
        namespace=config_app.get_k8s_velero_namespace(),
        plural=RESOURCES[ResourcesNames.BACKUP_STORAGE_LOCATION].plural,
    )

    current_default_bsl = None

    for bsl in bsl_list.get("items", []):
        if bsl.get("spec", {}).get("default", False):
            current_default_bsl = bsl["metadata"]["name"]
            break  # Troviamo solo il primo

    # Se esiste già un default, lo rimuoviamo
    if current_default_bsl and current_default_bsl != bsl_name:
        await remove_default_bsl_service(current_default_bsl)

    # Aggiorniamo il nuovo BSL con default=True
    patch_body = {
        "spec": {
            "default": True
        }
    }

    response = custom_objects.patch_namespaced_custom_object(
        group=VELERO["GROUP"],
        version=VELERO["VERSION"],
        namespace=config_app.get_k8s_velero_namespace(),
        plural=RESOURCES[ResourcesNames.BACKUP_STORAGE_LOCATION].plural,
        name=bsl_name,
        body=patch_body
    )
    return response


@trace_k8s_async_method(description="Remove default bsl")
async def remove_default_bsl_service(bsl_name: str):
    # Patch per rimuovere il default
    patch_body = {
        "spec": {
            "default": False
        }
    }

    response = custom_objects.patch_namespaced_custom_object(
        group=VELERO["GROUP"],
        version=VELERO["VERSION"],
        namespace=config_app.get_k8s_velero_namespace(),
        plural=RESOURCES[ResourcesNames.BACKUP_STORAGE_LOCATION].plural,
        name=bsl_name,
        body=patch_body
    )
    return response

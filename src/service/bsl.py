from models.k8s.bsl import BackupStorageLocationResponseSchema
from schemas.request.update_bsl import UpdateBslRequestSchema
from service.location_credentials import get_credential_service, get_default_credential_service

from schemas.request.create_bsl import CreateBslRequestSchema

from kubernetes import client

from utils.k8s_tracer import trace_k8s_async_method

from configs.config_boot import config_app
from constants.velero import VELERO
from constants.resources import RESOURCES, ResourcesNames

custom_objects = client.CustomObjectsApi()


@trace_k8s_async_method(description="Gets bsls service")
async def get_bsls_service():
    bsls = custom_objects.list_namespaced_custom_object(
        group=VELERO["GROUP"],
        version=VELERO["VERSION"],
        namespace=config_app.k8s.velero_namespace,
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
        namespace=config_app.k8s.velero_namespace,
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
            "objectStorage": {
                "bucket": bsl_data.bucket
            }
        }
    }

    if hasattr(bsl_data, "backupSyncPeriod") and bsl_data.backupSyncPeriod != '':
        bsl_body["spec"]["backupSyncPeriod"] = bsl_data.backupSyncPeriod

    if hasattr(bsl_data, "validationFrequency") and bsl_data.validationFrequency != '':
        bsl_body["spec"]["validationFrequency"] = bsl_data.validationFrequency

    if hasattr(bsl_data, "accessMode") and bsl_data.accessMode in ['ReadOnly', 'ReadWrite']:
        bsl_body["spec"]["accessMode"] = bsl_data.accessMode

    if hasattr(bsl_data, "prefix") and bsl_data.prefix and bsl_data.prefix.strip() != '':
        bsl_body["spec"]["objectStorage"]["prefix"] = bsl_data.prefix.strip()

    if hasattr(bsl_data, "config") and len(bsl_data.config) > 0:
        bsl_body["spec"]["config"] = bsl_data.config

    if (hasattr(bsl_data, "credentialName") and
            hasattr(bsl_data, "credentialKey") and
            bsl_data.credentialName and bsl_data.credentialName != '' and
            bsl_data.credentialKey and bsl_data.credentialKey != ''):
        bsl_body['spec']["credential"] = {
            "name": bsl_data.credentialName,
            "key": bsl_data.credentialKey
        }

    response = custom_objects.create_namespaced_custom_object(
        group=VELERO["GROUP"],
        version=VELERO["VERSION"],
        namespace=config_app.k8s.velero_namespace,
        plural=RESOURCES[ResourcesNames.BACKUP_STORAGE_LOCATION].plural,
        body=bsl_body
    )

    if bsl_data.default:
        await set_default_bsl_service(bsl_data.name)

    return response


@trace_k8s_async_method(description="Delete bsl")
async def delete_bsl_service(bsl_name: str):
    """Delete a Velero BSL"""
    response = custom_objects.delete_namespaced_custom_object(
        group=VELERO["GROUP"],
        version=VELERO["VERSION"],
        namespace=config_app.k8s.velero_namespace,
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
        namespace=config_app.k8s.velero_namespace,
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
        namespace=config_app.k8s.velero_namespace,
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
        namespace=config_app.k8s.velero_namespace,
        plural=RESOURCES[ResourcesNames.BACKUP_STORAGE_LOCATION].plural,
        name=bsl_name,
        body=patch_body
    )
    return response


@trace_k8s_async_method(description="Update a bsl")
async def update_bsl_service(bsl_data: UpdateBslRequestSchema):
    """
    Update a Backup Storage Location (BSL) in Kubernetes
    """

    existing_bsl = custom_objects.get_namespaced_custom_object(
        group=VELERO["GROUP"],
        version=VELERO["VERSION"],
        namespace=config_app.k8s.velero_namespace,
        plural=RESOURCES[ResourcesNames.BACKUP_STORAGE_LOCATION].plural,
        name=bsl_data.name
    )

    # Update the necessary fields

    if hasattr(bsl_data, "provider") and bsl_data.provider != '':
        existing_bsl["spec"]["provider"] = bsl_data.provider.strip()

    if hasattr(bsl_data, "bucket") and bsl_data.bucket != '':
        existing_bsl["spec"]["objectStorage"]["bucket"] = bsl_data.bucket.strip()

    if hasattr(bsl_data, "prefix") and bsl_data.prefix and bsl_data.prefix.strip() != '':
        existing_bsl['spec']['objectStorage']['prefix'] = bsl_data.prefix.strip()
    elif (hasattr(bsl_data, "prefix") and bsl_data.prefix.strip() == '' and
          'objectStorage' in existing_bsl["spec"] and 'prefix' in existing_bsl['spec']['objectStorage']):
        existing_bsl['spec']['objectStorage'].pop("prefix")

    if hasattr(bsl_data, "backupSyncPeriod") and bsl_data.backupSyncPeriod != '':
        existing_bsl["spec"]["backupSyncPeriod"] = bsl_data.backupSyncPeriod

    if hasattr(bsl_data, "validationFrequency") and bsl_data.validationFrequency != '':
        existing_bsl["spec"]["validationFrequency"] = bsl_data.validationFrequency

    if hasattr(bsl_data, "accessMode") and bsl_data.accessMode in ['ReadOnly', 'ReadWrite']:
        existing_bsl["spec"]["accessMode"] = bsl_data.accessMode

    if hasattr(bsl_data, "config") and len(bsl_data.config) > 0:
        existing_bsl["spec"]["config"] = bsl_data.config
    elif 'config' in existing_bsl["spec"]:
        existing_bsl["spec"].pop('config')

    if (hasattr(bsl_data, "credentialName") and
            hasattr(bsl_data, "credentialKey") and
            bsl_data.credentialName and bsl_data.credentialName != '' and
            bsl_data.credentialKey and bsl_data.credentialKey != ''):
        existing_bsl['spec']["credential"] = {
            "name": bsl_data.credentialName,
            "key": bsl_data.credentialKey
        }
    else:
        if "spec" in existing_bsl and isinstance(existing_bsl["spec"], dict) and 'credential' in existing_bsl["spec"]:
            existing_bsl['spec'].pop("credential")

    response = custom_objects.replace_namespaced_custom_object(
        group=VELERO["GROUP"],
        version=VELERO["VERSION"],
        namespace=config_app.k8s.velero_namespace,
        plural=RESOURCES[ResourcesNames.BACKUP_STORAGE_LOCATION].plural,
        name=bsl_data.name,
        body=existing_bsl
    )

    if bsl_data.default:
        await set_default_bsl_service(bsl_data.name)

    return response

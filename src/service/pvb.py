from fastapi import HTTPException
from kubernetes import client
from vui_common.configs.config_proxy import config_app


async def get_pod_volume_backups_service():
    # Create an instance of the API client
    api_instance = client.CustomObjectsApi()

    # Namespace in which Velero is operating
    namespace = config_app.k8s.velero_namespace

    # Get Velero's backup items
    group = "velero.io"
    version = "v1"
    plural = "podvolumebackups"

    try:
        # API call to get backups
        pvb = api_instance.list_namespaced_custom_object(group, version, namespace, plural)

        return pvb
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error {str(e)}")


async def get_pod_volume_backup_details_service(backup_name=None):
    # Create an instance of the API client
    api_instance = client.CustomObjectsApi()

    # Namespace in which Velero is operating
    namespace = config_app.k8s.velero_namespace

    # Group, version and plural to access Velero backups
    group = "velero.io"
    version = "v1"
    plural = "podvolumebackups"

    try:
        # API call to get backups
        pvb = api_instance.list_namespaced_custom_object(group, version, namespace, plural)

        # Filter objects by label velero.io/backup-uid
        filtered_items = [
            item for item in pvb.get('items', [])
            if item.get('metadata', {}).get('labels', {}).get('velero.io/backup-name') == backup_name
        ] if backup_name else pvb.get('items', [])

        # Return only filtered objects
        return filtered_items
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error {str(e)}")

async def get_pod_volume_restore_service():
    # Create an instance of the API client
    api_instance = client.CustomObjectsApi()

    # Namespace in which Velero is operating
    namespace = config_app.k8s.velero_namespace

    # Get Velero's backup items
    group = "velero.io"
    version = "v1"
    plural = "podvolumerestores"

    try:
        # API call to get backups
        pvb = api_instance.list_namespaced_custom_object(group, version, namespace, plural)

        return pvb
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error {str(e)}")

async def get_pod_volume_restore_details_service(restore_name=None):
    # Create an instance of the API client
    api_instance = client.CustomObjectsApi()

    # Namespace in which Velero is operating
    namespace = config_app.k8s.velero_namespace

    # Group, version and plural to access Velero backups
    group = "velero.io"
    version = "v1"
    plural = "podvolumerestores"

    try:
        # API call to get backups
        pvb = api_instance.list_namespaced_custom_object(group, version, namespace, plural)

        # Filter objects by label velero.io/backup-uid
        filtered_items = [
            item for item in pvb.get('items', [])
            if item.get('metadata', {}).get('labels', {}).get('velero.io/restore-name') == restore_name
        ] if restore_name else pvb.get('items', [])

        # Return only filtered objects
        return filtered_items
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error {str(e)}")

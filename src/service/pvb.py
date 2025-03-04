from fastapi import HTTPException
from kubernetes import client


async def get_pod_volume_backups_service():
    # Create an instance of the API client
    api_instance = client.CustomObjectsApi()

    # Namespace in which Velero is operating
    namespace = "velero"

    # Get Velero's backup items
    group = "velero.io"
    version = "v1"
    plural = "podvolumebackups"

    try:
        # API call to get backups
        backups = api_instance.list_namespaced_custom_object(group, version, namespace, plural)

        # Convert the result to JSON
        # backups_json = json.dumps(backups, indent=4)

        return backups
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error {str(e)}")


async def get_pod_volume_backup_details_service(backup_name=None):
    # Create an instance of the API client
    api_instance = client.CustomObjectsApi()

    # Namespace in which Velero is operating
    namespace = "velero"

    # Group, version and plural to access Velero backups
    group = "velero.io"
    version = "v1"
    plural = "podvolumebackups"

    try:
        # API call to get backups
        backups = api_instance.list_namespaced_custom_object(group, version, namespace, plural)

        # Filter objects by label velero.io/backup-uid
        filtered_items = [
            item for item in backups.get('items', [])
            if item.get('metadata', {}).get('labels', {}).get('velero.io/backup-name') == backup_name
        ] if backup_name else backups.get('items', [])

        # Return only filtered objects
        return filtered_items
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error {str(e)}")

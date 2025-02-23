import os
import json
from typing import List, Dict

from fastapi import HTTPException

from service.utils.download_request import (_create_download_request,
                                            _download_and_extract_backup,
                                            _cleanup_download_request)
from schemas.velero_storage_class import VeleroStorageClass


from utils.k8s_tracer import trace_k8s_async_method


@trace_k8s_async_method(description="Get backup storage classes")
async def get_backup_storage_classes_service(backup_name: str) -> VeleroStorageClass:
    """
    Retrieve the StorageClasses used in a Velero backup using a DownloadRequest.
    """

    # Create a DownloadRequest to retrieve backup data
    download_url = await _create_download_request(backup_name, "BackupContents")
    if not download_url:
        raise HTTPException(status_code=400, detail=f"Create a DownloadRequest to retrieve backup data")

    # Download and extract the file containing the Kubernetes manifest
    extracted_path = await _download_and_extract_backup(download_url)
    if not extracted_path:
        raise HTTPException(status_code=400, detail=f"Error while extracting backup '{backup_name}'")

    # Extracting StorageClasses from PVCs
    storage_classes = _extract_storage_classes_from_pvc_service(extracted_path)

    # Cleaning the DownloadRequest after use
    _cleanup_download_request(backup_name)

    if storage_classes:
        return VeleroStorageClass(storage_classes=storage_classes)

    return VeleroStorageClass(storage_classes=[])


@trace_k8s_async_method(description="Extract storage classes from pvc")
def _extract_storage_classes_from_pvc_service(extracted_path: str) -> List[Dict]:
    """
    Extracts StorageClasses from the manifest of PersistentVolumeClaims (PVCs).
    """
    storage_classes = []

    pvc_path = os.path.join(extracted_path, "resources", "persistentvolumeclaims", "namespaces")
    if not os.path.exists(pvc_path):
        return []

    for namespace in os.listdir(pvc_path):
        namespace_path = os.path.join(pvc_path, namespace)
        if not os.path.isdir(namespace_path):
            continue

        for pvc_file in os.listdir(namespace_path):
            pvc_file_path = os.path.join(namespace_path, pvc_file)
            try:
                with open(pvc_file_path, "r") as f:
                    pvc_data = json.load(f)

                if "spec" in pvc_data and "storageClassName" in pvc_data["spec"]:
                    storage_classes.append({"name": pvc_data["spec"]["storageClassName"]})

            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Error reading PVC {pvc_file_path}: {e}")

    return storage_classes

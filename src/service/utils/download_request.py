import time
import requests
import tempfile
import tarfile

from fastapi import HTTPException
from kubernetes import client
from typing import Optional

from configs.velero import VELERO
from configs.resources import RESOURCES, ResourcesNames
from configs.config_boot import config_app
from utils.logger_boot import logger

custom_objects = client.CustomObjectsApi()


async def create_download_request(resource_name: str, resource_kind: str) -> Optional[str]:
    """
    Creates a Velero DownloadRequest to download the requested data.
    If a request already exists, reuses or deletes it and creates a new one.

    :param resource_name: Name of the resource (e.g., backup_name).
    :param resource_kind: Type of the resource (BackupLog, BackupContents, etc.).
    :return: URL for download or None if it fails
    """
    logger.info(f"Create download request download-{resource_name}")
    download_request_name = f"download-{resource_name}"

    try:
        # Check if a DownloadRequest already exists
        existing_request = custom_objects.get_namespaced_custom_object(
            group=VELERO["GROUP"],
            version=VELERO["VERSION"],
            namespace=config_app.get_k8s_velero_namespace(),
            plural=RESOURCES[ResourcesNames.DOWNLOAD_REQUEST].plural,
            name=download_request_name
        )

        # If it exists and is Processed, we reuse its URL
        if existing_request.get("status", {}).get("phase") == "Processed":
            logger.info(f"Download request from existing url {existing_request.get('status', {}).get('downloadURL')}")
            return existing_request.get("status", {}).get("downloadURL")

        # If it exists but is not Processed, we delete it and recreate it
        logger.info(f"DownloadRequest ‘{download_request_name}’ already exists but is not Processed. By deleting it...")
        cleanup_download_request(resource_name)

    except client.exceptions.ApiException as e:
        if e.status != 404:  # Ignoriamo l'errore 404 (not found)
            logger.error(f"Error while checking DownloadRequest ‘{download_request_name}’: {e}")
            raise HTTPException(status_code=400,
                                detail=f"Error while checking DownloadRequest ‘{download_request_name}’: {e}")

    try:
        # Creating the new DownloadRequest
        logger.info("Creating the new DownloadRequest")
        download_request_body = {
            "apiVersion": f"{VELERO['GROUP']}/{VELERO['VERSION']}",
            "kind": "DownloadRequest",
            "metadata": {
                "name": download_request_name,
                "namespace": config_app.get_k8s_velero_namespace()
            },
            "spec": {
                "target": {
                    "kind": resource_kind,
                    "name": resource_name
                }
            }
        }

        custom_objects.create_namespaced_custom_object(
            group=VELERO["GROUP"],
            version=VELERO["VERSION"],
            namespace=config_app.get_k8s_velero_namespace(),
            plural=RESOURCES[ResourcesNames.DOWNLOAD_REQUEST].plural,
            body=download_request_body
        )

        # Wait up to 5 attempts for the request to be processed
        for _ in range(5):
            time.sleep(4)
            download_request = custom_objects.get_namespaced_custom_object(
                group=VELERO["GROUP"],
                version=VELERO["VERSION"],
                namespace=config_app.get_k8s_velero_namespace(),
                plural=RESOURCES[ResourcesNames.DOWNLOAD_REQUEST].plural,
                name=download_request_name
            )

            if download_request.get("status", {}).get("phase") == "Processed":
                return download_request.get("status", {}).get("downloadURL")

    except Exception as e:
        logger.error(f"Error in DownloadRequest for ‘{resource_name}’: {e}")
        raise HTTPException(status_code=400,
                            detail=f"Error in DownloadRequest for ‘{resource_name}’: {e}")


async def download_and_extract_backup(download_url: str) -> Optional[str]:
    """
    Downloads and extracts the backup containing Kubernetes manifest.

    :param download_url: URL of the file generated by Velero.
    :return: Path to the extracted folder or None if it fails
    """
    logger.info(f"Download and extract backup from {download_url}")
    try:
        response = requests.get(download_url, stream=True)
        if response.status_code != 200:
            logger.error(f"Backup download error: {response.status_code}")
            raise HTTPException(status_code=400,
                                detail=f"Backup download error: {response.status_code}")

        # Creating a temporary file for downloading
        with tempfile.NamedTemporaryFile(delete=False, suffix=".tar.gz") as temp_file:
            temp_file.write(response.content)
            temp_file_path = temp_file.name

        # Creating a temporary folder to extract the contents
        extract_folder = tempfile.mkdtemp()

        # Extract the contents of the tar.gz file
        with tarfile.open(temp_file_path, "r:gz") as tar:
            tar.extractall(path=extract_folder)

        return extract_folder

    except Exception as e:
        logger.error(f"Error while downloading and extracting backup: {e}")
        raise HTTPException(status_code=400,
                            detail=f"Error while downloading and extracting backup: {e}")


def cleanup_download_request(resource_name: str):
    """
    Deletes the DownloadRequest after use to avoid accumulation in the cluster.

    :param resource_name: Name of the resource associated with the DownloadRequest.
    """
    logger.info(f"Cleanup download request {resource_name}")
    download_request_name = f"download-{resource_name}"
    try:
        custom_objects.delete_namespaced_custom_object(
            group=VELERO["GROUP"],
            version=VELERO["VERSION"],
            namespace=config_app.get_k8s_velero_namespace(),
            plural=RESOURCES[ResourcesNames.DOWNLOAD_REQUEST].plural,
            name=download_request_name
        )
        logger.info(f"DownloadRequest '{download_request_name}' successfully deleted.")
    except client.exceptions.ApiException as e:
        if e.status == 404:
            logger.error(f"DownloadRequest '{download_request_name}' does not exist, no deletion required.")
            raise HTTPException(status_code=400,
                                detail=f"DownloadRequest '{download_request_name}' does not exist, no deletion "
                                       f"required.")

        else:
            logger.error(f"Error while deleting DownloadRequest '{download_request_name}': {e}")
            raise HTTPException(status_code=400,
                                detail=f"Error while deleting DownloadRequest '{download_request_name}': {e}")

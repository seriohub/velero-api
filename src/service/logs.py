from fastapi import HTTPException

import requests
import gzip
import tempfile

from schemas.velero_log import VeleroLog
from service.utils.download_request import create_download_request, cleanup_download_request
from utils.k8s_tracer import trace_k8s_async_method

VELERO_LOG_TYPES = {
    "backup": "BackupLog",
    "restore": "RestoreLog"
}

@trace_k8s_async_method(description="Get velero resource logs")
async def get_velero_logs_service(resource_name: str, resource_type: str) -> VeleroLog:
    """Retrieve logs from a Velero resource (Backup, Restore, etc.) using DownloadRequest"""
    if resource_type not in VELERO_LOG_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported resource type: {resource_type}")

    log_kind = VELERO_LOG_TYPES[resource_type]

    try:
        # Creation of the DownloadRequest or retrieval of the URL if already available
        log_url = await create_download_request(resource_name, log_kind)
        if not log_url:
            raise HTTPException(status_code=408, detail=f"Unable to retrieve log download URL")

        # Download and extract logs
        logs = await _download_and_extract_logs(log_url)

        # DownloadRequest cleanup to avoid buildup
        # cleanup_download_request(resource_name)
        return logs

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error {str(e)}")


async def _download_and_extract_logs(log_url: str) -> VeleroLog:
    """Download the .gz file, check the format, and return logs"""
    try:
        response = requests.get(log_url, stream=True)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail=f"Download error: {response.status_code}")

        # Check the type of content
        content_type = response.headers.get("Content-Type", "")
        if "application/gzip" not in content_type and "binary/octet-stream" not in content_type:
            raise HTTPException(status_code=400, detail=f"Invalid response: Content-Type {content_type}")

        with tempfile.NamedTemporaryFile(delete=True) as temp_file:
            temp_file.write(response.content)
            temp_file.flush()

            # Open the .gz file and read the contents
            with gzip.open(temp_file.name, "rb") as gz_file:
                log_content = gz_file.read().decode("utf-8").split("\n")

        return VeleroLog(success=True, logs=log_content)

    except Exception as e:
        raise HTTPException(status_code=408, detail=f"Request Timeout {str(e)}")

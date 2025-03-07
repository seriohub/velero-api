# from fastapi import HTTPException
from configs.config_boot import config_app
# from service.logs import _download_and_extract_logs
from service.utils.download_request import create_download_request, cleanup_download_request
from utils.k8s_tracer import trace_k8s_async_method
# import os
# import tempfile
# import requests
# import gzip
# import shutil
# from fastapi import HTTPException

import os
import requests
import shutil
import tarfile
from fastapi import HTTPException


@trace_k8s_async_method(description="Download backup")
async def inspect_download_backup_service(backup_name: str) -> bool:
    try:
        # Creation of the DownloadRequest or retrieval of the URL if already available
        backup_url = await create_download_request(backup_name, 'BackupContents')
        if not backup_url:
            raise HTTPException(status_code=408, detail=f"Unable to retrieve log download URL")

        # Download and extract logs
        await _download_and_extract_contents(backup_name, backup_url)

        # DownloadRequest cleanup to avoid buildup
        cleanup_download_request(backup_name)
        return True

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error {str(e)}")


async def _download_and_extract_contents(backup_name: str, log_url: str,
                                         extract_dir: str = config_app.app.inspect_folder) -> str:
    """
    Scarica un file .tar.gz, lo estrae in una cartella specifica e restituisce il percorso della cartella estratta.

    :param backup_name: Nome del backup per creare una sottocartella.
    :param log_url: URL del file .tar.gz da scaricare.
    :param extract_dir: Directory base in cui estrarre i file (di default ../tmp/velero_logs).
    :return: Percorso della cartella contenente i file estratti.
    """
    try:
        # Creazione della cartella specifica per il backup
        backup_dir = os.path.join(extract_dir, backup_name)
        os.makedirs(backup_dir, exist_ok=True)

        # Percorso dove salvare il file tar.gz
        tar_gz_path = os.path.join(backup_dir, f"{backup_name}.tar.gz")

        # Scaricare il file tar.gz
        response = requests.get(log_url, stream=True)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail=f"Download error: {response.status_code}")

        # Salvare il file tar.gz nella cartella specificata
        with open(tar_gz_path, "wb") as file:
            shutil.copyfileobj(response.raw, file)

        # Creazione della cartella di estrazione
        extracted_dir = os.path.join(backup_dir, "./")
        os.makedirs(extracted_dir, exist_ok=True)

        # Estrarre il contenuto del file .tar.gz
        with tarfile.open(tar_gz_path, "r:gz") as tar:
            tar.extractall(path=extracted_dir)

        # Opzionale: rimuovere il file tar.gz dopo l'estrazione per risparmiare spazio
        os.remove(tar_gz_path)

        return extracted_dir

    except Exception as e:
        raise HTTPException(status_code=408, detail=f"Request Timeout {str(e)}")

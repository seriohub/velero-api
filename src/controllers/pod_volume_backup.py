from fastapi.responses import JSONResponse

from schemas.response.successful_request import SuccessfulRequest

from service.k8s import get_pod_volume_backups_service, get_pod_volume_backup_service


async def get_pod_volume_backups_handler():
    payload = await get_pod_volume_backups_service()

    response = SuccessfulRequest(payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=200)


async def get_pod_volume_backup_handler(backup_name: str):
    payload = await get_pod_volume_backup_service(backup_name)

    response = SuccessfulRequest(payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=200)

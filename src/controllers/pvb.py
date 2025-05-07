from fastapi.responses import JSONResponse

from vui_common.schemas.response.successful_request import SuccessfulRequest

from service.pvb import (get_pod_volume_backups_service,
                         get_pod_volume_backup_details_service,
                         get_pod_volume_restore_service,
                         get_pod_volume_restore_details_service)


async def get_pod_volume_backups_handler():
    payload = await get_pod_volume_backups_service()
    items = payload['items']
    response = SuccessfulRequest(payload=items)
    return JSONResponse(content=response.model_dump(), status_code=200)


async def get_pod_volume_backup_details_handler(backup_name: str):
    payload = await get_pod_volume_backup_details_service(backup_name)

    response = SuccessfulRequest(payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=200)

async def get_pod_volume_restore_handler():
    payload = await get_pod_volume_restore_service()
    items = payload['items']
    response = SuccessfulRequest(payload=items)
    return JSONResponse(content=response.model_dump(), status_code=200)

async def get_pod_volume_restore_details_handler(backup_name: str):
    payload = await get_pod_volume_restore_details_service(backup_name)

    response = SuccessfulRequest(payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=200)
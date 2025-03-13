from fastapi.responses import JSONResponse

from schemas.request.delete_resource import DeleteResourceRequestSchema
from schemas.response.successful_request import SuccessfulRequest
from schemas.response.successful_restores import SuccessfulRestoreResponse
from service.requests import (get_server_status_requests_service,
                              get_download_requests_service,
                              get_delete_backup_requests_service, delete_download_requests_service)


async def get_server_status_requests_handler():
    payload = await get_server_status_requests_service()

    response = SuccessfulRestoreResponse(payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=200)


async def get_download_requests_handler():
    payload = await get_download_requests_service()

    response = SuccessfulRequest(payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=201)


async def get_delete_backup_handler():
    payload = await get_delete_backup_requests_service()

    response = SuccessfulRequest(payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=200)

async def delete_download_request_handler(request: DeleteResourceRequestSchema):
    payload = await delete_download_requests_service(request)

    response = SuccessfulRequest(payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=200)

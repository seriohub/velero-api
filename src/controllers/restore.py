from fastapi.responses import JSONResponse

from schemas.request.create_restore import CreateRestoreRequestSchema
from schemas.response.successful_request import SuccessfulRequest
from schemas.response.successful_restores import SuccessfulRestoreResponse
from schemas.notification import Notification

from service.restore import get_restores_service, create_restore_service, delete_restore_service


async def get_restores_handler(in_progress=False):
    payload = await get_restores_service(in_progress=in_progress)

    response = SuccessfulRestoreResponse(payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=200)


async def create_restore_handler(restore: CreateRestoreRequestSchema):
    payload = await create_restore_service(restore_data=restore)

    msg = Notification(title='Create Restore',
                       description=f"Restore from {restore.backupName} "
                                   f"{restore.name} created successfully",
                       type_='INFO')
    response = SuccessfulRequest(notifications=[msg], payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=201)


async def delete_restore_handler(restore_name: str):
    payload = await delete_restore_service(restore_name=restore_name)

    msg = Notification(title='Delete restore',
                       description=f"Restore {restore_name} deleted request done!",
                       type_='INFO')
    response = SuccessfulRequest(notifications=[msg], payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=200)

import json
from fastapi.responses import JSONResponse

from schemas.request.create_backup import CreateBackupRequestSchema
from schemas.request.create_backup_from_schedule import CreateBackupFromScheduleRequestSchema
from schemas.request.update_backup_expiration import UpdateBackupExpirationRequestSchema
from schemas.response.successful_request import SuccessfulRequest
from schemas.response.successful_backups import SuccessfulBackupResponse
from schemas.notification import Notification

from service.backup_storage_class import get_backup_storage_classes_service
from service.resource import get_resource_creation_settings_service
from service.backup import (get_backups_service,
                            delete_backup_service,
                            create_backup_service,
                            create_backup_from_schedule_service,
                            get_backup_expiration_service,
                            update_backup_expiration_service,
                            download_backup_service)
from service.inspect_download_backup import inspect_download_backup_service


async def get_creation_settings_handler():
    payload = await get_resource_creation_settings_service()

    response = SuccessfulRequest(payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=200)


async def get_backups_handler(schedule_name: str | None = None, latest_per_schedule: bool = False,
                              in_progress: bool = False):
    payload = await get_backups_service(schedule_name=schedule_name,
                                        latest_per_schedule=latest_per_schedule,
                                        in_progress=in_progress)

    response = SuccessfulBackupResponse(payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=200)


async def delete_backup_handler(backup_name: str):
    payload = await delete_backup_service(backup_name=backup_name)

    msg = Notification(title='Delete backup',
                       description=f'Backup {backup_name} deleted request done!',
                       type_='INFO')

    response = SuccessfulRequest(notifications=[msg], payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=200)


async def create_backup_handler(backup: CreateBackupRequestSchema):
    payload = await create_backup_service(backup_data=backup)

    msg = Notification(title='Create backup',
                       description=f"Backup {backup.name} created!",
                       type_='INFO')
    response = SuccessfulRequest(notifications=[msg], payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=201)


async def create_backup_from_schedule_handler(backup: CreateBackupFromScheduleRequestSchema):
    payload = await create_backup_from_schedule_service(schedule_name=backup.scheduleName)

    msg = Notification(title='Create backup from schedule',
                       description=f"Backup created!",
                       type_='INFO')
    response = SuccessfulRequest(notifications=[msg], payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=201)


async def update_backup_expiration_handler(ttl: UpdateBackupExpirationRequestSchema):
    payload = await update_backup_expiration_service(backup_name=ttl.backupName,
                                           expiration=ttl.expiration)

    msg = Notification(title='TTL Updated',
                       description=f"Backup {ttl.backupName} expiration updated!",
                       type_='INFO')
    response = SuccessfulRequest(notifications=[msg], payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=201)


async def get_backup_expiration_handler(backup_name: str):
    payload = await get_backup_expiration_service(backup_name=backup_name)

    response = SuccessfulRequest(payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=200)


async def get_backup_storage_classes_handler(backup_name: str):
    payload = await get_backup_storage_classes_service(backup_name=backup_name)

    response = SuccessfulRequest(payload=json.loads(payload.model_dump_json())['storage_classes'])
    return JSONResponse(content=response.model_dump(), status_code=200)


async def download_backup_handler(backup_name: str):
    payload = await download_backup_service(backup_name=backup_name)

    response = SuccessfulRequest(payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=200)


async def inspect_download_backup_handler(backup_name: str):
    payload = await inspect_download_backup_service(backup_name=backup_name)

    response = SuccessfulRequest(payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=200)

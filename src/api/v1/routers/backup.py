from fastapi import APIRouter, Depends, status

from constants.response import common_error_authenticated_response

from vui_common.security.helpers.rate_limiter import RateLimiter, LimiterRequests

from vui_common.utils.swagger import route_description
from vui_common.utils.exceptions import handle_exceptions_endpoint

from schemas.request.delete_resource import DeleteResourceRequestSchema
from vui_common.schemas.response.successful_request import SuccessfulRequest
from schemas.request.create_backup import CreateBackupRequestSchema
from schemas.request.create_backup_from_schedule import CreateBackupFromScheduleRequestSchema
from schemas.request.update_backup_expiration import UpdateBackupExpirationRequestSchema
from schemas.response.successful_backups import SuccessfulBackupResponse

from controllers.common import (get_resource_describe_handler,
                                get_resource_logs_handler)
from controllers.backup import (get_backups_handler,
                                get_backup_storage_classes_handler,
                                create_backup_handler,
                                get_creation_settings_handler,
                                delete_backup_handler,
                                create_backup_from_schedule_handler,
                                update_backup_expiration_handler,
                                get_backup_expiration_handler,
                                download_backup_handler,
                                inspect_download_backup_handler)

router = APIRouter()


tag_name = "Backups"
endpoint_limiter = LimiterRequests(tags=tag_name,
                                   default_key='L1')

# ------------------------------------------------------------------------------------------------
#             GET BACKUP LIST
# ------------------------------------------------------------------------------------------------


limiter_backups = endpoint_limiter.get_limiter_cust('backups')
route = '/backups'


@router.get(
    path=route,
    tags=[tag_name],
    summary='Get backups list',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter_backups.max_request,
                                  limiter_seconds=limiter_backups.seconds),
    dependencies=[Depends(RateLimiter(interval_seconds=limiter_backups.seconds,
                                      max_requests=limiter_backups.max_request))],
    response_model=SuccessfulBackupResponse,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_200_OK
)
@handle_exceptions_endpoint
async def get_backups(schedule_name: str | None = None,
                      only_last_for_schedule: bool = False,
                      in_progress: bool = False
                      ):
    return await get_backups_handler(schedule_name=schedule_name,
                                     latest_per_schedule=str(only_last_for_schedule).lower() == 'true',
                                     in_progress=str(in_progress).lower() == 'true')


# ------------------------------------------------------------------------------------------------
#             BACKUP LOGS
# ------------------------------------------------------------------------------------------------

limiter_logs = endpoint_limiter.get_limiter_cust('backup_logs')
route = '/backup/logs'


@router.get(
    path=route,
    tags=[tag_name],
    summary='Get backup logs',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter_logs.max_request,
                                  limiter_seconds=limiter_logs.seconds),
    dependencies=[Depends(RateLimiter(interval_seconds=limiter_logs.seconds,
                                      max_requests=limiter_logs.max_request))],
    response_model=SuccessfulRequest,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def get_backup_logs(resource_name: str):
    return await get_resource_logs_handler(resource_name=resource_name, resource_type='backup')


# ------------------------------------------------------------------------------------------------
#             BACKUP DESCRIBE
# ------------------------------------------------------------------------------------------------


limiter_desc = endpoint_limiter.get_limiter_cust('backup_describe')
route = '/backup/describe'


@router.get(
    path=route,
    tags=[tag_name],
    summary='Get backup detail',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter_desc.max_request,
                                  limiter_seconds=limiter_desc.seconds),
    dependencies=[Depends(RateLimiter(interval_seconds=limiter_desc.seconds,
                                      max_requests=limiter_desc.max_request))],
    response_model=SuccessfulRequest,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def get_backup_describe(resource_name: str):
    return await get_resource_describe_handler(resource_name=resource_name, resource_type='backup')


# ------------------------------------------------------------------------------------------------
#             DELETE BACKUP
# ------------------------------------------------------------------------------------------------


limiter_del = endpoint_limiter.get_limiter_cust('backup')
route = '/backup'


@router.delete(
    path=route,
    tags=[tag_name],
    summary='Delete a backup',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter_del.max_request,
                                  limiter_seconds=limiter_del.seconds),
    dependencies=[Depends(RateLimiter(interval_seconds=limiter_del.seconds,
                                      max_requests=limiter_del.max_request))],
    response_model=SuccessfulRequest,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def delete_backup(backup: DeleteResourceRequestSchema):
    return await delete_backup_handler(backup_name=backup.name)


# ------------------------------------------------------------------------------------------------
#             GET BACKUP ENVIRONMENT
# ------------------------------------------------------------------------------------------------


limiter_env = endpoint_limiter.get_limiter_cust('backup_environment')
route = '/backup/environment'


@router.get(
    path=route,
    tags=[tag_name],
    summary='Get environment for a backup',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter_env.max_request,
                                  limiter_seconds=limiter_env.seconds),
    dependencies=[Depends(RateLimiter(interval_seconds=limiter_env.seconds,
                                      max_requests=limiter_env.max_request))],
    response_model=SuccessfulRequest,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def get_settings_create():
    return await get_creation_settings_handler()


# ------------------------------------------------------------------------------------------------
#             CREATE A BACKUP
# ------------------------------------------------------------------------------------------------


limiter_create = endpoint_limiter.get_limiter_cust('backup')
route = '/backup'


@router.post(
    path=route,
    tags=[tag_name],
    summary='Create a backup',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter_create.max_request,
                                  limiter_seconds=limiter_create.seconds),
    dependencies=[Depends(RateLimiter(interval_seconds=limiter_create.seconds,
                                      max_requests=limiter_create.max_request))],
    response_model=SuccessfulRequest,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_201_CREATED)
@handle_exceptions_endpoint
async def create_backup(backup: CreateBackupRequestSchema):
    return await create_backup_handler(backup=backup)


# ------------------------------------------------------------------------------------------------
#             CREATE A BACKUP FROM SCHEDULE
# ------------------------------------------------------------------------------------------------


limiter_create_from_schedule = endpoint_limiter.get_limiter_cust('backup_crete_from_schedule')
route = '/backup/create-from-schedule'


@router.post(
    path=route,
    tags=[tag_name],
    summary='Create a backup from a schedule',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter_create_from_schedule.max_request,
                                  limiter_seconds=limiter_create_from_schedule.seconds),
    dependencies=[Depends(RateLimiter(interval_seconds=limiter_create_from_schedule.seconds,
                                      max_requests=limiter_create_from_schedule.max_request))],
    response_model=SuccessfulRequest,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_201_CREATED)
@handle_exceptions_endpoint
async def create_backup_from_schedule(backup: CreateBackupFromScheduleRequestSchema):
    return await create_backup_from_schedule_handler(backup=backup)


# ------------------------------------------------------------------------------------------------
#             GET BACKUP EXPIRATION
# ------------------------------------------------------------------------------------------------


limiter_expiration = endpoint_limiter.get_limiter_cust('backup_expiration')
route = '/backup/expiration'


@router.get(
    path=route,
    tags=[tag_name],
    summary='Get expiration time for a backup',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter_expiration.max_request,
                                  limiter_seconds=limiter_expiration.seconds),
    dependencies=[Depends(RateLimiter(interval_seconds=limiter_expiration.seconds,
                                      max_requests=limiter_expiration.max_request))],
    response_model=SuccessfulRequest,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def get_expiration(backup_name: str):
    return await get_backup_expiration_handler(backup_name)


# ------------------------------------------------------------------------------------------------
#             UPDATE BACKUP EXPIRATION
# ------------------------------------------------------------------------------------------------


limiter_update_expiration = endpoint_limiter.get_limiter_cust('backup_expiration')
route = '/backup/expiration'


@router.patch(
    path=route,
    tags=[tag_name],
    summary='Update expiration date for a backup',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter_update_expiration.max_request,
                                  limiter_seconds=limiter_update_expiration.seconds),
    dependencies=[Depends(RateLimiter(interval_seconds=limiter_update_expiration.seconds,
                                      max_requests=limiter_update_expiration.max_request))],
    response_model=SuccessfulRequest,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def update_backup_expiration(ttl: UpdateBackupExpirationRequestSchema):
    return await update_backup_expiration_handler(ttl=ttl)


# ------------------------------------------------------------------------------------------------
#             GET BACKUP STORAGE CLASSES
# ------------------------------------------------------------------------------------------------


limiter_storage_classes = endpoint_limiter.get_limiter_cust('backup_storage_classes')
route = '/backup/storage-classes'


@router.get(
    path=route,
    tags=[tag_name],
    summary='Get backup storage classes',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter_storage_classes.max_request,
                                  limiter_seconds=limiter_storage_classes.seconds),
    dependencies=[Depends(RateLimiter(interval_seconds=limiter_storage_classes.seconds,
                                      max_requests=limiter_storage_classes.max_request))],
    response_model=SuccessfulRequest,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def get_backup_storage_classes(backup_name: str):
    return await get_backup_storage_classes_handler(backup_name)

# ------------------------------------------------------------------------------------------------
#             DOWNLOAD BACKUP
# ------------------------------------------------------------------------------------------------


limiter_storage_classes = endpoint_limiter.get_limiter_cust('backup_download')
route = '/backup/download'


@router.get(
    path=route,
    tags=[tag_name],
    summary='Download backup',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter_storage_classes.max_request,
                                  limiter_seconds=limiter_storage_classes.seconds),
    dependencies=[Depends(RateLimiter(interval_seconds=limiter_storage_classes.seconds,
                                      max_requests=limiter_storage_classes.max_request))],
    response_model=SuccessfulRequest,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def download_backup(backup_name: str):
    return await download_backup_handler(backup_name)

# ------------------------------------------------------------------------------------------------
#             DOWNLOAD BACKUP
# ------------------------------------------------------------------------------------------------


limiter_storage_classes = endpoint_limiter.get_limiter_cust('backup_download')
route = '/backup/inspect-download'


@router.get(
    path=route,
    tags=[tag_name],
    summary='Download for inspect',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter_storage_classes.max_request,
                                  limiter_seconds=limiter_storage_classes.seconds),
    dependencies=[Depends(RateLimiter(interval_seconds=limiter_storage_classes.seconds,
                                      max_requests=limiter_storage_classes.max_request))],
    response_model=SuccessfulRequest,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def inspect_download_backup(backup_name: str):
    return await inspect_download_backup_handler(backup_name)

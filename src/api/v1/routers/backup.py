from fastapi import APIRouter, Request, status, Depends
from typing import Union

from core.config import ConfigHelper
from security.service.helpers.rate_limiter import RateLimiter, LimiterRequests

from utils.commons import route_description
from utils.handle_exceptions import handle_exceptions_endpoint
from helpers.printer import PrintHelper

from api.v1.schemas.create_backup import CreateBackup

from api.common.response_model.failed_request import FailedRequest
from api.common.response_model.successful_request import SuccessfulRequest

from api.v1.controllers.backup import Backup

router = APIRouter()
backup = Backup()

config_app = ConfigHelper()
print_ls = PrintHelper('[v1.routers.backup_location]',
                       level=config_app.get_internal_log_level())

tag_name = "Backups"

endpoint_limiter = LimiterRequests(printer=print_ls,
                                   tags=tag_name,
                                   default_key='L1')

limiter = endpoint_limiter.get_limiter_cust('backup_get')
route = '/backup/get'


@router.get(path=route,
            tags=[tag_name],
            summary='Get backups list',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter.max_request,
                                          limiter_seconds=limiter.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter.seconds,
                                              max_requests=limiter.max_request))],
            response_model=Union[SuccessfulRequest, FailedRequest],
            status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def backup_get(schedule_name=None, only_last_for_schedule='', in_progress=False):
    return await backup.get(schedule_name=schedule_name,
                            only_last_for_schedule=only_last_for_schedule.lower() == 'true',
                            in_progress=in_progress == 'true')


limiter_logs = endpoint_limiter.get_limiter_cust('backup_logs')
route = '/backup/logs'


@router.get(path=route,
            tags=[tag_name],
            summary='Get backups logs',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter_logs.max_request,
                                          limiter_seconds=limiter_logs.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_logs.seconds,
                                              max_requests=limiter_logs.max_request))],
            response_model=Union[SuccessfulRequest, FailedRequest],
            status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def backup_logs(resource_name=None):
    return await backup.logs(resource_name)


limiter_des = endpoint_limiter.get_limiter_cust('backup_describe')
route = '/backup/describe'


@router.get(path=route,
            tags=[tag_name],
            summary='Get backups detail',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter_des.max_request,
                                          limiter_seconds=limiter_des.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_des.seconds,
                                              max_requests=limiter_des.max_request))],
            response_model=Union[SuccessfulRequest, FailedRequest],
            status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def backup_describe(resource_name=None):
    return await backup.describe(resource_name)


limiter_del = endpoint_limiter.get_limiter_cust('backup_delete')
route = '/backup/delete'


@router.get(path=route,
            tags=[tag_name],
            summary='Delete a backup',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter_del.max_request,
                                          limiter_seconds=limiter_del.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_del.seconds,
                                              max_requests=limiter_del.max_request))],
            response_model=Union[SuccessfulRequest, FailedRequest],
            status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def backup_delete(resource_name=None):
    return await backup.delete(resource_name)


limiter_setting = endpoint_limiter.get_limiter_cust('backup_create_settings')
route = '/backup/create/settings'


@router.get(path=route,
            tags=[tag_name],
            summary='Create a setting for a backup',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter_setting.max_request,
                                          limiter_seconds=limiter_setting.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_setting.seconds,
                                              max_requests=limiter_setting.max_request))],
            response_model=Union[SuccessfulRequest, FailedRequest],
            status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def get_settings_create():
    return await backup.get_settings_create()


limiter_create = endpoint_limiter.get_limiter_cust('backup_create')
route = '/backup/create'


@router.post(path=route,
             tags=[tag_name],
             summary='Create a backup',
             description=route_description(tag=tag_name,
                                           route=route,
                                           limiter_calls=limiter_create.max_request,
                                           limiter_seconds=limiter_create.seconds),
             dependencies=[Depends(RateLimiter(interval_seconds=limiter_create.seconds,
                                               max_requests=limiter_create.max_request))],
             response_model=Union[SuccessfulRequest, FailedRequest],
             status_code=status.HTTP_201_CREATED)
@handle_exceptions_endpoint
async def create(create_backup: CreateBackup):
    return await backup.create(info=create_backup)


limiter_create_from_schedule = endpoint_limiter.get_limiter_cust('backup_crete_from_schedule')
route = '/backup/create-from-schedule'


@router.post(path=route,
             tags=[tag_name],
             summary='Create a backup from a schedule',
             description=route_description(tag=tag_name,
                                           route=route,
                                           limiter_calls=limiter_create_from_schedule.max_request,
                                           limiter_seconds=limiter_create_from_schedule.seconds),
             dependencies=[Depends(RateLimiter(interval_seconds=limiter_create_from_schedule.seconds,
                                               max_requests=limiter_create_from_schedule.max_request))],
             status_code=status.HTTP_201_CREATED)
@handle_exceptions_endpoint
async def create_from_schedule(info: Request):
    req_info = await info.json()
    return await backup.create_from_schedule(req_info)


limiter_expiration = endpoint_limiter.get_limiter_cust('backup_get_expiration')
route = '/backup/get-expiration'


@router.get(path=route,
            tags=['Backup'],
            summary='Get expiration time for a specific backup',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter_expiration.max_request,
                                          limiter_seconds=limiter_expiration.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_expiration.seconds,
                                              max_requests=limiter_expiration.max_request))],
            status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def get_expiration(backup_name=None):
    return await backup.get_expiration(backup_name)


limiter_update_expiration = endpoint_limiter.get_limiter_cust('backup_update_expiration')
route = '/backup/update-expiration'


@router.get(path=route,
            tags=['Backup'],
            summary='Update expiration date for a backup',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter_update_expiration.max_request,
                                          limiter_seconds=limiter_update_expiration.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_update_expiration.seconds,
                                              max_requests=limiter_update_expiration.max_request))],
            status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def update_expiration(backup_name=None, expiration=None):
    return await backup.update_expiration(backup_name, expiration)


limiter_storage_classes = endpoint_limiter.get_limiter_cust('backup_get_storage_classes')
route = '/backup/get-storage-classes'


@router.get(path=route,
            tags=['Backup'],
            summary='Get backup storage classes',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter_storage_classes.max_request,
                                          limiter_seconds=limiter_storage_classes.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_storage_classes.seconds,
                                              max_requests=limiter_storage_classes.max_request))],
            status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def get_backup_storage_classes(backup_name=None):
    return await backup.get_backup_storage_classes(backup_name)

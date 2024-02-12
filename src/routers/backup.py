from fastapi import APIRouter, Depends

from helpers.commons import route_description
from helpers.handle_exceptions import *
from helpers.printer_helper import PrintHelper
from libs.backup import Backup
from fastapi import Request
from libs.security.rate_limiter import RateLimiter, LimiterRequests

router = APIRouter()
tag_name = "Backup"
backup = Backup()
print_ls = PrintHelper('routes.backup_location_v1')

endpoint_limiter = LimiterRequests(debug=False,
                                   printer=print_ls,
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
                                              max_requests=limiter.max_request))])
@handle_exceptions_async_method
async def backup_get(schedule_name=None, only_last_for_schedule='', in_progress=False):
    return await backup.get(schedule_name=schedule_name,
                            only_last_for_schedule=only_last_for_schedule.lower() == 'true',
                            in_progress=in_progress)


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
                                              max_requests=limiter_logs.max_request))])
@handle_exceptions_async_method
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
                                              max_requests=limiter_des.max_request))])
@handle_exceptions_async_method
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
                                              max_requests=limiter_del.max_request))])
@handle_exceptions_async_method
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
                                              max_requests=limiter_setting.max_request))])
@handle_exceptions_async_method
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
                                               max_requests=limiter_create.max_request))])
@handle_exceptions_async_method
async def create(info: Request):
    req_info = await info.json()
    return await backup.create(req_info)


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
                                               max_requests=limiter_create_from_schedule.max_request))])
@handle_exceptions_async_method
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
                                              max_requests=limiter_expiration.max_request))])
@handle_exceptions_async_method
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
                                              max_requests=limiter_update_expiration.max_request))])
@handle_exceptions_async_method
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
                                              max_requests=limiter_storage_classes.max_request))])
@handle_exceptions_async_method
async def get_backup_storage_classes(backup_name=None):
    return await backup.get_backup_storage_classes(backup_name)

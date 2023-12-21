from fastapi import APIRouter

from helpers.handle_exceptions import *
from libs.backup_v1 import BackupV1
from fastapi import Request

router = APIRouter()

backup = BackupV1()


@router.get('/backup/get')
@handle_exceptions_async_method
async def backup_get(schedule_name=None, only_last_for_schedule='', in_progress=False):
    return await backup.get(schedule_name=schedule_name,
                            only_last_for_schedule=only_last_for_schedule.lower() == 'true',
                            in_progress=in_progress)


@router.get('/backup/logs')
@handle_exceptions_async_method
async def backup_logs(resource_name=None):
    return await backup.logs(resource_name)


@router.get('/backup/describe')
@handle_exceptions_async_method
async def backup_describe(resource_name=None):
    return await backup.describe(resource_name)


@router.get('/backup/delete')
@handle_exceptions_async_method
async def backup_delete(resource_name=None):
    return await backup.delete(resource_name)


@router.get('/backup/create/settings')
@handle_exceptions_async_method
async def get_settings_create():
    return await backup.get_settings_create()


@router.post('/backup/create')
@handle_exceptions_async_method
async def create(info: Request):
    req_info = await info.json()
    return await backup.create(req_info)


@router.post('/backup/create-from-schedule')
@handle_exceptions_async_method
async def create_from_schedule(info: Request):
    req_info = await info.json()
    return await backup.create_from_schedule(req_info)


@router.get('/backup/get-expiration')
@handle_exceptions_async_method
async def get_expiration(backup_name=None):
    return await backup.get_expiration(backup_name)


@router.get('/backup/update-expiration')
@handle_exceptions_async_method
async def update_expiration(backup_name=None, expiration=None):
    return await backup.update_expiration(backup_name, expiration)

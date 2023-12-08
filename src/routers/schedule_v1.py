from fastapi import APIRouter
from fastapi import Request

from helpers.handle_exceptions import *
from libs.schedule_v1 import ScheduleV1
from libs.backup_v1 import BackupV1

router = APIRouter()

schedule = ScheduleV1()
backup = BackupV1()


@router.get('/schedule/get')
@handle_exceptions_async_method
async def schedule_get():
    return await schedule.get()


@router.get('/schedule/create/settings')
@handle_exceptions_async_method
async def get_settings_create():
    return await backup.get_settings_create()


@router.post('/schedule/create')
@handle_exceptions_async_method
async def create(info: Request):
    req_info = await info.json()
    return await schedule.create(req_info)


@router.get('/schedule/describe')
@handle_exceptions_async_method
async def schedule_describe(resource_name=None):
    return await schedule.describe(resource_name)


@router.get('/schedule/unpause')
@handle_exceptions_async_method
async def schedule_describe(resource_name=None):
    return await schedule.unpause(resource_name)


@router.get('/schedule/pause')
@handle_exceptions_async_method
async def schedule_describe(resource_name=None):
    return await schedule.pause(resource_name)


@router.get('/schedule/delete')
@handle_exceptions_async_method
async def schedule_delete(resource_name=None):
    return await schedule.delete(resource_name)


@router.post('/schedule/update')
@handle_exceptions_async_method
async def create(info: Request):
    req_info = await info.json()
    return await schedule.update(req_info)

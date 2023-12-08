from fastapi import APIRouter
from fastapi import Request

from helpers.handle_exceptions import *
from libs.restore_v1 import RestoreV1

router = APIRouter()

restore = RestoreV1()


@router.get('/restore/get')
@handle_exceptions_async_method
async def restore_get(in_progress=''):
    return await restore.get(in_progress=in_progress.lower() == 'true')


@router.get('/restore/logs')
@handle_exceptions_async_method
async def restore_logs(resource_name=None):
    return await restore.logs(resource_name)


@router.get('/restore/describe')
@handle_exceptions_async_method
async def restore_describe(resource_name=None):
    return await restore.describe(resource_name)


@router.get('/restore/delete')
@handle_exceptions_async_method
async def restore_delete(resource_name=None):
    return await restore.delete(resource_name)


@router.post('/restore/create')
@handle_exceptions_async_method
async def restore_create(info: Request):
    req_info = await info.json()
    return await restore.create(req_info)

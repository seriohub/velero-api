from fastapi import APIRouter, Depends
from fastapi import Request
from helpers.handle_exceptions import *
from helpers.printer_helper import PrintHelper
from libs.restore import Restore
from libs.security.rate_limiter import RateLimiter, LimiterRequests


router = APIRouter()
restore = Restore()
print_ls = PrintHelper('routes.restore_v1')

endpoint_limiter = LimiterRequests(debug=False,
                                   printer=print_ls,
                                   tags='Restore',
                                   default_key='L1')
limiter = endpoint_limiter.get_limiter_cust("restore_get")


@router.get('/restore/get',
            tags=['Restore'],
            summary='Get backups repository',
            dependencies=[Depends(RateLimiter(interval_seconds=limiter.seconds,
                                              max_requests=limiter.max_request))])
@handle_exceptions_async_method
async def restore_get(in_progress=''):
    return await restore.get(in_progress=in_progress.lower() == 'true')


limiter_logs = endpoint_limiter.get_limiter_cust('restore_logs')


@router.get('/restore/logs',
            tags=['Restore'],
            summary='Get logs for restore operation',
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_logs.seconds,
                                              max_requests=limiter_logs.max_request))])
@handle_exceptions_async_method
async def restore_logs(resource_name=None):
    return await restore.logs(resource_name)


limiter_des = endpoint_limiter.get_limiter_cust('restore_describe')


@router.get('/restore/describe',
            tags=['Restore'],
            summary='Get detail for restore operation',
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_des.seconds,
                                              max_requests=limiter_des.max_request))])
@handle_exceptions_async_method
async def restore_describe(resource_name=None):
    return await restore.describe(resource_name)


limiter_delete = endpoint_limiter.get_limiter_cust('restore_delete')


@router.get('/restore/delete',
            tags=['Restore'],
            summary='Delete restore operation',
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_delete.seconds,
                                              max_requests=limiter_delete.max_request))])
@handle_exceptions_async_method
async def restore_delete(resource_name=None):
    return await restore.delete(resource_name)


limiter_create = endpoint_limiter.get_limiter_cust('restore_create')


@router.post('/restore/create',
             tags=['Restore'],
             summary='Create a new restore',
             dependencies=[Depends(RateLimiter(interval_seconds=limiter_create.seconds,
                                               max_requests=limiter_create.max_request))])
@handle_exceptions_async_method
async def restore_create(info: Request):
    req_info = await info.json()
    return await restore.create(req_info)

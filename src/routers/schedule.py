from fastapi import APIRouter, Depends
from fastapi import Request
from helpers.handle_exceptions import *
from helpers.printer_helper import PrintHelper

from libs.schedule import Schedule
from libs.backup import Backup
from libs.security.rate_limiter import RateLimiter, LimiterRequests

router = APIRouter()
rate_limiter = RateLimiter()
schedule = Schedule()
backup = Backup()

print_ls = PrintHelper('routes.schedule_v1')

endpoint_limiter = LimiterRequests(debug=False,
                                   printer=print_ls,
                                   tags='Schedule',
                                   default_key='L1')
limiter = endpoint_limiter.get_limiter_cust('schedule_get')


@router.get('/schedule/get',
            tags=['Schedule'],
            summary='Get schedules details',
            dependencies=[Depends(RateLimiter(interval_seconds=limiter.seconds,
                                              max_requests=limiter.max_request))])
@handle_exceptions_async_method
async def schedule_get():
    return await schedule.get()


limiter_cs = endpoint_limiter.get_limiter_cust('schedule_create_settings')


@router.get('/schedule/create/settings',
            tags=['Schedule'],
            summary='Create a new setting for schedule',
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_cs.seconds,
                                              max_requests=limiter_cs.max_request))])
@handle_exceptions_async_method
async def get_settings_create():
    return await backup.get_settings_create()


limiter_c = endpoint_limiter.get_limiter_cust('schedule_create')


@router.post('/schedule/create',
             tags=['Schedule'],
             summary='Create a new schedule',
             dependencies=[Depends(RateLimiter(interval_seconds=limiter_c.seconds,
                                               max_requests=limiter_c.max_request))])
@handle_exceptions_async_method
async def create(info: Request):
    req_info = await info.json()
    return await schedule.create(req_info)


limiter_des = endpoint_limiter.get_limiter_cust('schedule_describe')


@router.get('/schedule/describe',
            tags=['Schedule'],
            summary='Get details for a schedule',
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_des.seconds,
                                              max_requests=limiter_des.max_request))])
@handle_exceptions_async_method
async def schedule_describe(resource_name=None):
    return await schedule.describe(resource_name)


limiter_up = endpoint_limiter.get_limiter_cust('schedule_unpause')


@router.get('/schedule/unpause',
            tags=['Schedule'],
            summary='Set unpause a schedule',
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_up.seconds,
                                              max_requests=limiter_up.max_request))])
@handle_exceptions_async_method
async def schedule_describe(resource_name=None):
    return await schedule.unpause(resource_name)


limiter_p = endpoint_limiter.get_limiter_cust('schedule_pause')


@router.get('/schedule/pause',
            tags=['Schedule'],
            summary='Set in pause aschedule',
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_p.seconds,
                                              max_requests=limiter_p.max_request))])
@handle_exceptions_async_method
async def schedule_describe(resource_name=None):
    return await schedule.pause(resource_name)


limiter_delete = endpoint_limiter.get_limiter_cust('schedule_delete')


@router.get('/schedule/delete',
            tags=['Schedule'],
            summary='Delete a schedule',
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_delete.seconds,
                                              max_requests=limiter_delete.max_request))])
@handle_exceptions_async_method
async def schedule_delete(resource_name=None):
    return await schedule.delete(resource_name)


limiter_update = endpoint_limiter.get_limiter_cust('schedule_update')


@router.post('/schedule/update',
             tags=['Schedule'],
             summary='Create a schedule',
             dependencies=[Depends(RateLimiter(interval_seconds=limiter_update.seconds,
                                               max_requests=limiter_update.max_request))])
@handle_exceptions_async_method
async def create(info: Request):
    req_info = await info.json()
    return await schedule.update(req_info)

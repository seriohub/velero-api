from fastapi import APIRouter, Depends
from fastapi import Request

from helpers.commons import route_description
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
tag_name = 'Schedule'
endpoint_limiter = LimiterRequests(debug=False,
                                   printer=print_ls,
                                   tags=tag_name,
                                   default_key='L1')
limiter = endpoint_limiter.get_limiter_cust('schedule_get')
route = '/schedule/get'


@router.get(path=route,
            tags=[tag_name],
            summary='Get schedules details',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter.max_request,
                                          limiter_seconds=limiter.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter.seconds,
                                              max_requests=limiter.max_request))])
@handle_exceptions_async_method
async def schedule_get():
    return await schedule.get()


limiter_cs = endpoint_limiter.get_limiter_cust('schedule_create_settings')
route = '/schedule/create/settings'


@router.get(path=route,
            tags=[tag_name],
            summary='Create a new setting for schedule',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter_cs.max_request,
                                          limiter_seconds=limiter_cs.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_cs.seconds,
                                              max_requests=limiter_cs.max_request))])
@handle_exceptions_async_method
async def get_settings_create():
    return await backup.get_settings_create()


limiter_c = endpoint_limiter.get_limiter_cust('schedule_create')
route = '/schedule/create'


@router.post(path=route,
             tags=[tag_name],
             summary='Create a new schedule',
             description=route_description(tag=tag_name,
                                           route=route,
                                           limiter_calls=limiter_c.max_request,
                                           limiter_seconds=limiter_c.seconds),

             dependencies=[Depends(RateLimiter(interval_seconds=limiter_c.seconds,
                                               max_requests=limiter_c.max_request))])
@handle_exceptions_async_method
async def create(info: Request):
    req_info = await info.json()
    return await schedule.create(req_info)


limiter_des = endpoint_limiter.get_limiter_cust('schedule_describe')
route = '/schedule/describe'


@router.get(path=route,
            tags=[tag_name],
            summary='Get details for a schedule',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter_des.max_request,
                                          limiter_seconds=limiter_des.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_des.seconds,
                                              max_requests=limiter_des.max_request))])
@handle_exceptions_async_method
async def schedule_describe(resource_name=None):
    return await schedule.describe(resource_name)


limiter_up = endpoint_limiter.get_limiter_cust('schedule_unpause')
route = '/schedule/unpause'


@router.get(path=route,
            tags=[tag_name],
            summary='Set unpause a schedule',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter_up.max_request,
                                          limiter_seconds=limiter_up.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_up.seconds,
                                              max_requests=limiter_up.max_request))])
@handle_exceptions_async_method
async def schedule_describe(resource_name=None):
    return await schedule.unpause(resource_name)


limiter_p = endpoint_limiter.get_limiter_cust('schedule_pause')
route = '/schedule/pause'


@router.get(path=route,
            tags=[tag_name],
            summary='Set in pause aschedule',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter_p.max_request,
                                          limiter_seconds=limiter_p.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_p.seconds,
                                              max_requests=limiter_p.max_request))])
@handle_exceptions_async_method
async def schedule_describe(resource_name=None):
    return await schedule.pause(resource_name)


limiter_delete = endpoint_limiter.get_limiter_cust('schedule_delete')
route = '/schedule/delete'


@router.get(path=route,
            tags=[tag_name],
            summary='Delete a schedule',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter_delete.max_request,
                                          limiter_seconds=limiter_delete.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_delete.seconds,
                                              max_requests=limiter_delete.max_request))])
@handle_exceptions_async_method
async def schedule_delete(resource_name=None):
    return await schedule.delete(resource_name)


limiter_update = endpoint_limiter.get_limiter_cust('schedule_update')
route = '/schedule/update'


@router.post(path=route,
             tags=[tag_name],
             summary='Create a schedule',
             description=route_description(tag=tag_name,
                                           route=route,
                                           limiter_calls=limiter_update.max_request,
                                           limiter_seconds=limiter_update.seconds),
             dependencies=[Depends(RateLimiter(interval_seconds=limiter_update.seconds,
                                               max_requests=limiter_update.max_request))])
@handle_exceptions_async_method
async def create(info: Request):
    req_info = await info.json()
    return await schedule.update(req_info)

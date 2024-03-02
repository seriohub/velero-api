from fastapi import APIRouter, Request, status, Depends
from typing import Union

from core.config import ConfigHelper
from security.rate_limiter import RateLimiter, LimiterRequests

from helpers.printer import PrintHelper
from utils.commons import route_description
from utils.handle_exceptions import handle_exceptions_endpoint

from api.v1.schemas.create_schedule import CreateSchedule

from api.common.response_model.failed_request import FailedRequest
from api.common.response_model.successful_request import SuccessfulRequest

from api.v1.controllers.schedule import Schedule
from api.v1.controllers.backup import Backup

router = APIRouter()
rate_limiter = RateLimiter()
schedule = Schedule()
backup = Backup()
config_app = ConfigHelper()
print_ls = PrintHelper('[v1.routers.schedule]',
                       level=config_app.get_internal_log_level())

tag_name = 'Schedule'
endpoint_limiter = LimiterRequests(printer=print_ls,
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
                                              max_requests=limiter.max_request))],
            response_model=Union[SuccessfulRequest, FailedRequest],
            status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
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
                                              max_requests=limiter_cs.max_request))],
            response_model=Union[SuccessfulRequest, FailedRequest],
            status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
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
                                               max_requests=limiter_c.max_request))],
             response_model=Union[SuccessfulRequest, FailedRequest],
             status_code=status.HTTP_201_CREATED)
@handle_exceptions_endpoint
async def create(create_schedule: CreateSchedule):
    return await schedule.create(create_schedule)


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
                                              max_requests=limiter_des.max_request))],
            response_model=Union[SuccessfulRequest, FailedRequest],
            status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
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
                                              max_requests=limiter_up.max_request))],
            response_model=Union[SuccessfulRequest, FailedRequest],
            status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
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
                                              max_requests=limiter_p.max_request))],
            response_model=Union[SuccessfulRequest, FailedRequest],
            status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
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
                                              max_requests=limiter_delete.max_request))],
            response_model=Union[SuccessfulRequest, FailedRequest],
            status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
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
                                               max_requests=limiter_update.max_request))],
             response_model=Union[SuccessfulRequest, FailedRequest],
             status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def update(info: Request):
    req_info = await info.json()
    return await schedule.update(req_info)

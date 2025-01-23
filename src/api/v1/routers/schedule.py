from fastapi import APIRouter, Request, status, Depends
from typing import Union

from core.config import ConfigHelper
from security.service.helpers.rate_limiter import RateLimiter, LimiterRequests

from helpers.printer import PrintHelper
from utils.commons import route_description
from utils.handle_exceptions import handle_exceptions_endpoint

from api.v1.schemas.create_schedule import CreateSchedule
from api.v1.schemas.delete_schedule import DeleteSchedule
from api.v1.schemas.update_schedule import UpdateSchedule
from api.v1.schemas.pause_unpause_schedule import PauseUnpauseSchedule

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

tag_name = 'Schedules'
endpoint_limiter = LimiterRequests(printer=print_ls,
                                   tags=tag_name,
                                   default_key='L1')

limiter_schedules = endpoint_limiter.get_limiter_cust('schedules')
route = '/schedules'
@router.get(path=route,
            tags=[tag_name],
            summary='Get schedules',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter_schedules.max_request,
                                          limiter_seconds=limiter_schedules.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_schedules.seconds,
                                              max_requests=limiter_schedules.max_request))],
            response_model=Union[SuccessfulRequest, FailedRequest],
            status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def schedule_get():
    return await schedule.get()


limiter_env = endpoint_limiter.get_limiter_cust('schedule_environment')
route = '/schedule/environment'
@router.get(path=route,
            tags=[tag_name],
            summary='Create environment for schedule',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter_env.max_request,
                                          limiter_seconds=limiter_env.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_env.seconds,
                                              max_requests=limiter_env.max_request))],
            response_model=Union[SuccessfulRequest, FailedRequest],
            status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def get_settings_create():
    return await backup.get_settings_create()


limiter_create = endpoint_limiter.get_limiter_cust('schedule')
route = '/schedule'
@router.post(path=route,
             tags=[tag_name],
             summary='Create a new schedule',
             description=route_description(tag=tag_name,
                                           route=route,
                                           limiter_calls=limiter_create.max_request,
                                           limiter_seconds=limiter_create.seconds),

             dependencies=[Depends(RateLimiter(interval_seconds=limiter_create.seconds,
                                               max_requests=limiter_create.max_request))],
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
@router.patch(path=route,
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
async def schedule_unpause(schedule_status: PauseUnpauseSchedule):
    return await schedule.unpause(schedule=schedule_status)


limiter_p = endpoint_limiter.get_limiter_cust('schedule_pause')
route = '/schedule/pause'
@router.patch(path=route,
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
async def schedule_pause(schedule_status: PauseUnpauseSchedule):
    return await schedule.pause(schedule=schedule_status)


limiter_delete = endpoint_limiter.get_limiter_cust('schedule')
route = '/schedule'
@router.delete(path=route,
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
async def schedule_delete(delete_schedule: DeleteSchedule):
    return await schedule.delete(delete_schedule=delete_schedule)


limiter_update = endpoint_limiter.get_limiter_cust('schedule')
route = '/schedule'
@router.put(path=route,
            tags=[tag_name],
            summary='Update a schedule',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter_update.max_request,
                                          limiter_seconds=limiter_update.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_update.seconds,
                                              max_requests=limiter_update.max_request))],
            response_model=Union[SuccessfulRequest, FailedRequest],
            status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def update(update_schedule: UpdateSchedule):
    return await schedule.update(update_schedule=update_schedule)

# limiter_backups = endpoint_limiter.get_limiter_cust('schedule_manifest')
# route = '/schedule/manifest'
# @router.get(path=route,
#             tags=[tag_name],
#             summary='Get schedule manifest',
#             description=route_description(tag=tag_name,
#                                           route=route,
#                                           limiter_calls=limiter_backups.max_request,
#                                           limiter_seconds=limiter_backups.seconds),
#             dependencies=[Depends(RateLimiter(interval_seconds=limiter_backups.seconds,
#                                               max_requests=limiter_backups.max_request))],
#             response_model=Union[SuccessfulRequest, FailedRequest],
#             status_code=status.HTTP_200_OK)
# @handle_exceptions_endpoint
# async def get_manifest(schedule_name=None):
#     return await schedule.get_manifest(schedule_name=schedule_name)
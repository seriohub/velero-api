from fastapi import APIRouter, status, Depends

from constants.response import common_error_authenticated_response
from schemas.request.pause_schedule import PauseScheduleRequestSchema

from security.helpers.rate_limiter import RateLimiter, LimiterRequests

from schemas.request.delete_resource import DeleteResourceRequestSchema
from schemas.response.successful_schedules import SuccessfulScheduleResponse
from schemas.request.create_schedule import CreateScheduleRequestSchema
from schemas.request.update_schedule import UpdateScheduleRequestSchema
from schemas.response.successful_request import SuccessfulRequest

from utils.swagger import route_description
from utils.exceptions import handle_exceptions_endpoint

from controllers.backup import get_creation_settings_handler
from controllers.common import get_resource_describe_handler
from controllers.schedule import (get_schedules_handler,
                                  create_schedule_handler,
                                  unpause_schedule_handler,
                                  pause_schedule_handler,
                                  delete_schedule_handler, update_schedule_handler)

router = APIRouter()
rate_limiter = RateLimiter()



tag_name = 'Schedules'
endpoint_limiter = LimiterRequests(tags=tag_name,
                                   default_key='L1')

# ------------------------------------------------------------------------------------------------
#             GET SCHEDULE LIST
# ------------------------------------------------------------------------------------------------


limiter_schedules = endpoint_limiter.get_limiter_cust('schedules')
route = '/schedules'


@router.get(
    path=route,
    tags=[tag_name],
    summary='Get schedules',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter_schedules.max_request,
                                  limiter_seconds=limiter_schedules.seconds),
    dependencies=[Depends(RateLimiter(interval_seconds=limiter_schedules.seconds,
                                      max_requests=limiter_schedules.max_request))],
    response_model=SuccessfulScheduleResponse,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def get_schedule():
    return await get_schedules_handler()


# ------------------------------------------------------------------------------------------------
#             GET SCHEDULE ENVIRONMENT
# ------------------------------------------------------------------------------------------------


limiter_env = endpoint_limiter.get_limiter_cust('schedule_environment')
route = '/schedule/environment'


@router.get(
    path=route,
    tags=[tag_name],
    summary='Create environment for schedule',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter_env.max_request,
                                  limiter_seconds=limiter_env.seconds),
    dependencies=[Depends(RateLimiter(interval_seconds=limiter_env.seconds,
                                      max_requests=limiter_env.max_request))],
    response_model=SuccessfulRequest,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def get_creation_settings():
    return await get_creation_settings_handler()


# ------------------------------------------------------------------------------------------------
#             CREATE A SCHEDULE
# ------------------------------------------------------------------------------------------------


limiter_create = endpoint_limiter.get_limiter_cust('schedule')
route = '/schedule'


@router.post(
    path=route,
    tags=[tag_name],
    summary='Create a new schedule',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter_create.max_request,
                                  limiter_seconds=limiter_create.seconds),

    dependencies=[Depends(RateLimiter(interval_seconds=limiter_create.seconds,
                                      max_requests=limiter_create.max_request))],
    response_model=SuccessfulRequest,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_201_CREATED)
@handle_exceptions_endpoint
async def create_schedule(schedule: CreateScheduleRequestSchema):
    return await create_schedule_handler(schedule)


# ------------------------------------------------------------------------------------------------
#             GET SCHEDULE DESCRIBE
# ------------------------------------------------------------------------------------------------


limiter_des = endpoint_limiter.get_limiter_cust('schedule_describe')
route = '/schedule/describe'


@router.get(
    path=route,
    tags=[tag_name],
    summary='Get details for a schedule',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter_des.max_request,
                                  limiter_seconds=limiter_des.seconds),
    dependencies=[Depends(RateLimiter(interval_seconds=limiter_des.seconds,
                                      max_requests=limiter_des.max_request))],
    response_model=SuccessfulRequest,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def schedule_describe(resource_name: str):
    return await get_resource_describe_handler(resource_name=resource_name, resource_type='schedule')


# ------------------------------------------------------------------------------------------------
#             SET SCHEDULE DISABLED
# ------------------------------------------------------------------------------------------------


limiter_up = endpoint_limiter.get_limiter_cust('schedule_unpause')
route = '/schedule/unpause'


@router.patch(
    path=route,
    tags=[tag_name],
    summary='Set unpause a schedule',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter_up.max_request,
                                  limiter_seconds=limiter_up.seconds),
    dependencies=[Depends(RateLimiter(interval_seconds=limiter_up.seconds,
                                      max_requests=limiter_up.max_request))],
    response_model=SuccessfulRequest,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def unpause_schedule(schedule: PauseScheduleRequestSchema):
    return await unpause_schedule_handler(schedule=schedule.name)


# ------------------------------------------------------------------------------------------------
#             SET SCHEDULE ENABLED
# ------------------------------------------------------------------------------------------------


limiter_p = endpoint_limiter.get_limiter_cust('schedule_pause')
route = '/schedule/pause'


@router.patch(
    path=route,
    tags=[tag_name],
    summary='Set in pause aschedule',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter_p.max_request,
                                  limiter_seconds=limiter_p.seconds),
    dependencies=[Depends(RateLimiter(interval_seconds=limiter_p.seconds,
                                      max_requests=limiter_p.max_request))],
    response_model=SuccessfulRequest,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def pause_schedule(schedule: PauseScheduleRequestSchema):
    return await pause_schedule_handler(schedule=schedule.name)


# ------------------------------------------------------------------------------------------------
#             DELETE A SCHEDULE
# ------------------------------------------------------------------------------------------------


limiter_delete = endpoint_limiter.get_limiter_cust('schedule')
route = '/schedule'


@router.delete(
    path=route,
    tags=[tag_name],
    summary='Delete a schedule',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter_delete.max_request,
                                  limiter_seconds=limiter_delete.seconds),
    dependencies=[Depends(RateLimiter(interval_seconds=limiter_delete.seconds,
                                      max_requests=limiter_delete.max_request))],
    response_model=SuccessfulRequest,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def delete_schedule(schedule: DeleteResourceRequestSchema):
    return await delete_schedule_handler(schedule_name=schedule.name)


# ------------------------------------------------------------------------------------------------
#             UPDATE A SCHEDULE
# ------------------------------------------------------------------------------------------------


limiter_update = endpoint_limiter.get_limiter_cust('schedule')
route = '/schedule'


@router.put(
    path=route,
    tags=[tag_name],
    summary='Update a schedule',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter_update.max_request,
                                  limiter_seconds=limiter_update.seconds),
    dependencies=[Depends(RateLimiter(interval_seconds=limiter_update.seconds,
                                      max_requests=limiter_update.max_request))],
    response_model=SuccessfulRequest,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def update_schedule(schedule: UpdateScheduleRequestSchema):
    return await update_schedule_handler(schedule=schedule)

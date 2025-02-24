from fastapi import APIRouter, status, Depends

from constants.response import common_error_authenticated_response

from security.helpers.rate_limiter import RateLimiter, LimiterRequests

from utils.swagger import route_description
from utils.exceptions import handle_exceptions_endpoint

from schemas.response.successful_request import SuccessfulRequest

from controllers.stats import (get_stats_handler,
                               get_in_progress_task_handler,
                               get_schedules_heatmap_handler)

router = APIRouter()
rate_limiter = RateLimiter()



tag_name = 'Statistics'
endpoint_limiter = LimiterRequests(tags=tag_name,
                                   default_key='L1')

# ------------------------------------------------------------------------------------------------
#             GET VELERO STATS
# ------------------------------------------------------------------------------------------------


limiter = endpoint_limiter.get_limiter_cust('utilis_stats')
route = '/stats'


@router.get(
    path=route,
    tags=[tag_name],
    summary='Get backups repository',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter.max_request,
                                  limiter_seconds=limiter.seconds),
    dependencies=[Depends(RateLimiter(interval_seconds=limiter.seconds,
                                      max_requests=limiter.max_request))],
    response_model=SuccessfulRequest,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def get_velero_stats():
    return await get_stats_handler()


# ------------------------------------------------------------------------------------------------
#             GET TASK IN PROGRESS
# ------------------------------------------------------------------------------------------------


limiter_inprog = endpoint_limiter.get_limiter_cust('utilis_in_progress')
route = '/stats/in-progress'


@router.get(
    path=route,
    tags=[tag_name],
    summary='Get operations in progress',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter_inprog.max_request,
                                  limiter_seconds=limiter_inprog.seconds),
    dependencies=[Depends(RateLimiter(interval_seconds=limiter_inprog.seconds,
                                      max_requests=limiter_inprog.max_request))],
    response_model=SuccessfulRequest,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def get_in_progress_task():
    return await get_in_progress_task_handler()


# ------------------------------------------------------------------------------------------------
#             GET SCHEDULE STATS
# ------------------------------------------------------------------------------------------------


limiter_schedules = endpoint_limiter.get_limiter_cust('stats_schedules')
route = '/stats/schedules'


@router.get(
    path=route,
    tags=[tag_name],
    summary='Get schedules stats',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter_inprog.max_request,
                                  limiter_seconds=limiter_inprog.seconds),
    dependencies=[Depends(RateLimiter(interval_seconds=limiter_inprog.seconds,
                                      max_requests=limiter_inprog.max_request))],
    response_model=SuccessfulRequest,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def get_schedules_heatmap():
    return await get_schedules_heatmap_handler()

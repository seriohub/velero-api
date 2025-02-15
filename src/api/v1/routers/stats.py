from fastapi import APIRouter, status, Depends
from typing import Union

from core.config import ConfigHelper
from security.helpers.rate_limiter import RateLimiter, LimiterRequests

from utils.commons import route_description
from utils.handle_exceptions import handle_exceptions_endpoint

from api.common.response_model.failed_request import FailedRequest
from api.common.response_model.successful_request import SuccessfulRequest

from api.v1.controllers.stats import Stats

router = APIRouter()
rate_limiter = RateLimiter()
utils_controller = Stats()
config_app = ConfigHelper()

tag_name = 'Statistics'
endpoint_limiter = LimiterRequests(tags=tag_name,
                                   default_key='L1')

limiter = endpoint_limiter.get_limiter_cust('utilis_stats')
route = '/stats'


@router.get(path=route,
            tags=[tag_name],
            summary='Get backups repository',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter.max_request,
                                          limiter_seconds=limiter.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter.seconds,
                                              max_requests=limiter.max_request))],
            response_model=Union[SuccessfulRequest, FailedRequest],
            status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def stats():
    return await utils_controller.stats()


limiter_inprog = endpoint_limiter.get_limiter_cust('utilis_in_progress')
route = '/stats/in-progress'


@router.get(path=route,
            tags=[tag_name],
            summary='Get operations in progress',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter_inprog.max_request,
                                          limiter_seconds=limiter_inprog.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_inprog.seconds,
                                              max_requests=limiter_inprog.max_request))],
            response_model=Union[SuccessfulRequest, FailedRequest],
            status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def in_progress():
    return await utils_controller.in_progress()


limiter_schedules = endpoint_limiter.get_limiter_cust('stats_schedules')
route = '/stats/schedules'


@router.get(path=route,
            tags=[tag_name],
            summary='Get schedules stats',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter_inprog.max_request,
                                          limiter_seconds=limiter_inprog.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_inprog.seconds,
                                              max_requests=limiter_inprog.max_request))],
            response_model=Union[SuccessfulRequest, FailedRequest],
            status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def schedules():
    return await utils_controller.schedules()

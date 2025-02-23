from fastapi import APIRouter, Depends, status

from typing import Union

from utils.commons import route_description
from utils.handle_exceptions import handle_exceptions_endpoint

from security.helpers.rate_limiter import LimiterRequests
from security.helpers.rate_limiter import RateLimiter

from schemas.response.failed_request import FailedRequest
from schemas.response.successful_request import SuccessfulRequest

from controllers.agent import watchdog_online_handler

router = APIRouter()

tag_name = "Agent"
endpoint_limiter = LimiterRequests(tags=tag_name,
                                   default_key='L1')

# ------------------------------------------------------------------------------------------------
#             GET WATCHDOG INFO
# ------------------------------------------------------------------------------------------------


limiter_watchdog = endpoint_limiter.get_limiter_cust('info_watchdog')
route = '/watchdog'


@router.get(path=route,
            tags=[tag_name],
            summary='Get info watchdog',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter_watchdog.max_request,
                                          limiter_seconds=limiter_watchdog.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_watchdog.seconds,
                                              max_requests=limiter_watchdog.max_request))],
            response_model=Union[SuccessfulRequest, FailedRequest],
            status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def watchdog_config():
    return await watchdog_online_handler()

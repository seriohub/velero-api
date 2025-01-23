from fastapi import APIRouter, Depends, status

from typing import Union

from core.config import ConfigHelper

from utils.commons import route_description
from utils.handle_exceptions import handle_exceptions_endpoint
from helpers.printer import PrintHelper

from security.service.helpers.rate_limiter import LimiterRequests
from security.service.helpers.rate_limiter import RateLimiter

from api.common.response_model.failed_request import FailedRequest
from api.common.response_model.successful_request import SuccessfulRequest


from api.common.controllers.agent import Agent
from service.watchdog_service import WatchdogService

router = APIRouter()

agent = Agent()
watchdogService = WatchdogService()

config_app = ConfigHelper()
print_ls = PrintHelper('[common.routers.agent]',
                       level=config_app.get_internal_log_level())

tag_name = "Agent"
endpoint_limiter = LimiterRequests(printer=print_ls,
                                   tags=tag_name,
                                   default_key='L1')

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
    return await agent.watchdog_online()

from fastapi import APIRouter, Request, status, Depends
from typing import Union

from core.config import ConfigHelper
from security.service.helpers.rate_limiter import RateLimiter, LimiterRequests

from utils.commons import route_description
from utils.handle_exceptions import handle_exceptions_endpoint
from helpers.printer import PrintHelper

from api.common.response_model.failed_request import FailedRequest
from api.common.response_model.successful_request import SuccessfulRequest

from api.v1.controllers.watchdog import Watchdog

router = APIRouter()
rate_limiter = RateLimiter()
watchdog = Watchdog()
config_app = ConfigHelper()
print_ls = PrintHelper('[v1.routers.watchdog]',
                       level=config_app.get_internal_log_level())

tag_name = 'Watchdog'

endpoint_limiter_setup = LimiterRequests(printer=print_ls,
                                         tags=tag_name,
                                         default_key='L1')
limiter_setup = endpoint_limiter_setup.get_limiter_cust('watchdog_info')
route = '/watchdog/info'


@router.get(path=route,
            tags=[tag_name],
            summary='Get info watchdog',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter_setup.max_request,
                                          limiter_seconds=limiter_setup.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_setup.seconds,
                                              max_requests=limiter_setup.max_request))],
            response_model=Union[SuccessfulRequest, FailedRequest],
            status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def watchdog_config():
    return await watchdog.version()


limiter_v = endpoint_limiter_setup.get_limiter_cust('watchdog_send_report')
route = '/watchdog/send-report'
@router.post(path=route,
             tags=[tag_name],
             summary='Send report',
             description=route_description(tag=tag_name,
                                           route=route,
                                           limiter_calls=limiter_v.max_request,
                                           limiter_seconds=limiter_v.seconds),
             dependencies=[Depends(RateLimiter(interval_seconds=limiter_v.seconds,
                                               max_requests=limiter_v.max_request))],
             response_model=Union[SuccessfulRequest, FailedRequest],
             status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def send_report():
    return await watchdog.send_report()


limiter_setup = endpoint_limiter_setup.get_limiter_cust('watchdog_config')
route = '/watchdog/config'
@router.get(path=route,
            tags=[tag_name],
            summary='Get all env variables',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter_setup.max_request,
                                          limiter_seconds=limiter_setup.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_setup.seconds,
                                              max_requests=limiter_setup.max_request))],
            response_model=Union[SuccessfulRequest, FailedRequest],
            status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def app_config():
    return await watchdog.get_env()


limiter_setup = endpoint_limiter_setup.get_limiter_cust('watchdog_cron')
route = '/watchdog/cron'
@router.get(path=route,
            tags=[tag_name],
            summary='Get cron',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter_setup.max_request,
                                          limiter_seconds=limiter_setup.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_setup.seconds,
                                              max_requests=limiter_setup.max_request))],
            response_model=Union[SuccessfulRequest, FailedRequest],
            status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def app_config():
    return await watchdog.get_cron()


limiter_v = endpoint_limiter_setup.get_limiter_cust('watchdog_send-test-notification')
route = '/watchdog/send-test-notification'
@router.post(path=route,
             tags=[tag_name],
             summary='Send a test message to verify channel settings',
             description=route_description(tag=tag_name,
                                           route=route,
                                           limiter_calls=limiter_v.max_request,
                                           limiter_seconds=limiter_v.seconds),
             dependencies=[Depends(RateLimiter(interval_seconds=limiter_v.seconds,
                                               max_requests=limiter_v.max_request))],
             response_model=Union[SuccessfulRequest, FailedRequest],
             status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def send_test_notification(info: Request):
    req_info = await info.json()
    # email: bool = True,
    # telegram: bool = True,
    # slack: bool = True
    return await watchdog.send_test_notification(req_info['email'],
                                                 req_info['telegram'],
                                                 req_info['slack'])

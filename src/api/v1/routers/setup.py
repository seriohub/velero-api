from fastapi import APIRouter, status, Depends
from typing import Union

from core.config import ConfigHelper
from security.rate_limiter import RateLimiter, LimiterRequests

from utils.commons import route_description
from utils.handle_exceptions import handle_exceptions_endpoint
from helpers.printer import PrintHelper

from api.common.response_model.failed_request import FailedRequest
from api.common.response_model.successful_request import SuccessfulRequest

from api.v1.controllers.setup import Setup

router = APIRouter()
rate_limiter = RateLimiter()
setup = Setup()
config_app = ConfigHelper()
print_ls = PrintHelper('[v1.routers.utils]',
                       level=config_app.get_internal_log_level())

tag_name = 'Setup'

endpoint_limiter_setup = LimiterRequests(printer=print_ls,
                                         tags=tag_name,
                                         default_key='L1')
limiter_setup = endpoint_limiter_setup.get_limiter_cust('Setup')
route = '/setup/get-config'


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
    return await setup.get_env()


limiter_v = endpoint_limiter_setup.get_limiter_cust('setup_version')
route = '/setup/version'


@router.get(path=route,
            tags=[tag_name],
            summary='Get velero client version',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter_v.max_request,
                                          limiter_seconds=limiter_v.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_v.seconds,
                                              max_requests=limiter_v.max_request))],
            response_model=Union[SuccessfulRequest, FailedRequest],
            status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def version():
    return await setup.version()

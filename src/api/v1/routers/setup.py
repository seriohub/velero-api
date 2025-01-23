from fastapi import APIRouter, status, Depends
from typing import Union

from core.config import ConfigHelper
from security.service.helpers.rate_limiter import RateLimiter, LimiterRequests

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

tag_name = 'Agent settings'

endpoint_limiter_setup = LimiterRequests(printer=print_ls,
                                         tags=tag_name,
                                         default_key='L1')
limiter_env = endpoint_limiter_setup.get_limiter_cust('settings_environment')
route = '/settings/environment'
@router.get(path=route,
            tags=[tag_name],
            summary='Get all environment variables',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter_env.max_request,
                                          limiter_seconds=limiter_env.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_env.seconds,
                                              max_requests=limiter_env.max_request))],
            response_model=Union[SuccessfulRequest, FailedRequest],
            status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def app_config():
    return await setup.get_env()


limiter_versions = endpoint_limiter_setup.get_limiter_cust('settings_version')
route = '/settings/velero'
@router.get(path=route,
            tags=[tag_name],
            summary='Get velero server and client version',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter_versions.max_request,
                                          limiter_seconds=limiter_versions.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_versions.seconds,
                                              max_requests=limiter_versions.max_request))],
            response_model=Union[SuccessfulRequest, FailedRequest],
            status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def version():
    return await setup.version()

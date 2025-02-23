from fastapi import APIRouter, status, Depends

from configs.response import common_error_authenticated_response

from security.helpers.rate_limiter import RateLimiter, LimiterRequests

from utils.commons import route_description
from utils.handle_exceptions import handle_exceptions_endpoint

from schemas.response.successful_request import SuccessfulRequest

from controllers.setup import (get_env_handler,
                               get_velero_version_handler)

from configs.config_boot import config_app

router = APIRouter()
rate_limiter = RateLimiter()


tag_name = 'Agent settings'

endpoint_limiter_setup = LimiterRequests(tags=tag_name,
                                         default_key='L1')

# ------------------------------------------------------------------------------------------------
#             GET ENVIRONMENT SETTINGS
# ------------------------------------------------------------------------------------------------

limiter_env = endpoint_limiter_setup.get_limiter_cust('settings_environment')
route = '/settings/environment'


@router.get(
    path=route,
    tags=[tag_name],
    summary='Get all environment variables',
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
async def get_environment():
    return await get_env_handler()


# ------------------------------------------------------------------------------------------------
#             GET DEPLOYED VELERO VERSION
# ------------------------------------------------------------------------------------------------


limiter_versions = endpoint_limiter_setup.get_limiter_cust('settings_version')
route = '/settings/velero'


@router.get(
    path=route,
    tags=[tag_name],
    summary='Get velero server and client version',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter_versions.max_request,
                                  limiter_seconds=limiter_versions.seconds),
    dependencies=[Depends(RateLimiter(interval_seconds=limiter_versions.seconds,
                                      max_requests=limiter_versions.max_request))],
    response_model=SuccessfulRequest,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def get_velero_version():
    return await get_velero_version_handler()

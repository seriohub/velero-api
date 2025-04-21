from fastapi import APIRouter, status, Depends

from constants.response import common_error_authenticated_response
from controllers.k8s import get_pod_logs_handler

from vui_common.security.helpers.rate_limiter import RateLimiter, LimiterRequests

from vui_common.utils.swagger import route_description
from vui_common.utils.exceptions import handle_exceptions_endpoint

from vui_common.schemas.response.successful_request import SuccessfulRequest

from controllers.setup import (get_env_handler,
                               get_velero_version_handler,
                               get_velero_pods_handler,
                               get_vui_pods_handler)

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
#             GET VELERO PODS
# ------------------------------------------------------------------------------------------------


limiter_versions = endpoint_limiter_setup.get_limiter_cust('vui_pods')
route = '/vui/pods'


@router.get(
    path=route,
    tags=[tag_name],
    summary='Get vui pods',
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
async def get_vui_pods():
    return await get_vui_pods_handler()

tag_name = 'Velero'

# ------------------------------------------------------------------------------------------------
#             GET DEPLOYED VELERO VERSION
# ------------------------------------------------------------------------------------------------


limiter_versions = endpoint_limiter_setup.get_limiter_cust('velero_version')
route = '/velero/version'


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


# ------------------------------------------------------------------------------------------------
#             GET VELERO PODS
# ------------------------------------------------------------------------------------------------


limiter_versions = endpoint_limiter_setup.get_limiter_cust('velero_pods')
route = '/velero/pods'


@router.get(
    path=route,
    tags=[tag_name],
    summary='Get velero pods',
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
async def get_velero_pods():
    return await get_velero_pods_handler()

# ------------------------------------------------------------------------------------------------
#             GET K8S POD LOGS
# ------------------------------------------------------------------------------------------------


limiter_logs = endpoint_limiter_setup.get_limiter_cust('k8s_pod_logs')
route = '/k8s/pod/logs'


@router.get(
    path=route,
    tags=[tag_name],
    summary='Get logs for the current pod',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter_logs.max_request,
                                  limiter_seconds=limiter_logs.seconds),
    dependencies=[Depends(RateLimiter(interval_seconds=limiter_logs.seconds,
                                      max_requests=limiter_logs.max_request))],
    response_model=SuccessfulRequest,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_200_OK
)
@handle_exceptions_endpoint
async def get_pod_logs(pod: str, target: str = 'velero', lines: int = 100):
    return await get_pod_logs_handler(target=target, pod=pod, lines=lines)

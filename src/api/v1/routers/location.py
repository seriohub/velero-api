from fastapi import APIRouter, Depends, status

from constants.response import common_error_authenticated_response

from vui_common.security.helpers.rate_limiter import RateLimiter, LimiterRequests

from vui_common.utils.swagger import route_description
from vui_common.utils.exceptions import handle_exceptions_endpoint

from vui_common.schemas.response.successful_request import SuccessfulRequest
from schemas.request.create_cloud_credentials import CreateCloudCredentialsRequestSchema

from controllers.k8s import (create_cloud_credentials_handler,
                             get_default_credential_handler,
                             get_credential_handler,
                             get_velero_secret_handler,
                             get_velero_secret_key_handler)

router = APIRouter()

tag_name = 'Locations'
endpoint_limiter = LimiterRequests(tags=tag_name,
                                   default_key='L1')

# ------------------------------------------------------------------------------------------------
#             GET VELERO LOCATION'S CREDENTIAL
# ------------------------------------------------------------------------------------------------


limiter_cg = endpoint_limiter.get_limiter_cust('location_credentials')
route = '/location/credentials'


@router.get(
    path=route,
    tags=[tag_name],
    summary='Get credential',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter_cg.max_request,
                                  limiter_seconds=limiter_cg.seconds),
    dependencies=[Depends(RateLimiter(interval_seconds=limiter_cg.seconds,
                                      max_requests=limiter_cg.max_request))],
    response_model=SuccessfulRequest,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_200_OK
)
@handle_exceptions_endpoint
async def get_credential(secret_name=None, secret_key=None):
    return await get_credential_handler(secret_name, secret_key)


# ------------------------------------------------------------------------------------------------
#             GET VELERO LOCATION CLOUD CREDENTIAL
# ------------------------------------------------------------------------------------------------


limiter_def_cg = endpoint_limiter.get_limiter_cust('location_cloud_credentials')
route = '/location/cloud-credentials'


@router.get(
    path=route,
    tags=[tag_name],
    summary='Get default credential',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter_def_cg.max_request,
                                  limiter_seconds=limiter_def_cg.seconds),
    dependencies=[Depends(RateLimiter(interval_seconds=limiter_def_cg.seconds,
                                      max_requests=limiter_def_cg.max_request))],
    response_model=SuccessfulRequest,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_200_OK
)
@handle_exceptions_endpoint
async def get_default_credential():
    return await get_default_credential_handler()


# ------------------------------------------------------------------------------------------------
#             VELERO CREATE LOCATION CREDENTIAL
# ------------------------------------------------------------------------------------------------


limiter_create_cr = endpoint_limiter.get_limiter_cust('location_create_credentials')
route = '/location/create-credentials'


@router.post(
    path=route,
    tags=[tag_name],
    summary='Send report',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter_create_cr.max_request,
                                  limiter_seconds=limiter_create_cr.seconds),
    dependencies=[Depends(RateLimiter(interval_seconds=limiter_create_cr.seconds,
                                      max_requests=limiter_create_cr.max_request))],
    response_model=SuccessfulRequest,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def create_credentials(cloud_credentials: CreateCloudCredentialsRequestSchema):
    return await create_cloud_credentials_handler(cloud_credentials=cloud_credentials)


# ------------------------------------------------------------------------------------------------
#             GET VELERO SECRETS NAME
# ------------------------------------------------------------------------------------------------


limiter_logs = endpoint_limiter.get_limiter_cust('k8s_velero_secret')
route = '/k8s/velero/secrets'


@router.get(
    path=route,
    tags=[tag_name],
    summary='Get velero secret',
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
async def get_velero_secret():
    return await get_velero_secret_handler()


# ------------------------------------------------------------------------------------------------
#             GET VELERO SECRET'S KEY
# ------------------------------------------------------------------------------------------------


limiter_logs = endpoint_limiter.get_limiter_cust('k8s_velero_secret_key')
route = '/k8s/velero/secret/key'


@router.get(
    path=route,
    tags=[tag_name],
    summary='Get velero secret\'s key',
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
async def get_velero_secret_key(secret_name):
    return await get_velero_secret_key_handler(secret_name)

from fastapi import APIRouter, Depends, status

from constants.response import common_error_authenticated_response

from security.helpers.rate_limiter import RateLimiter, LimiterRequests

from utils.swagger import route_description
from utils.exceptions import handle_exceptions_endpoint

from schemas.response.successful_request import SuccessfulRequest
from schemas.request.delete_resource import DeleteResourceRequestSchema

from controllers.vsl import (get_vsl_handler,
                             create_vsl_handler,
                             delete_vsl_handler)

from schemas.request.create_vsl import CreateVslRequestSchema

router = APIRouter()
rate_limiter = RateLimiter()


tag_name = 'Volume Snapshot Locations'
endpoint_limiter = LimiterRequests(tags=tag_name,
                                   default_key='L1')

# ------------------------------------------------------------------------------------------------
#             GET VOLUME SNAPSHOT LOCATIONS LIST
# ------------------------------------------------------------------------------------------------


limiter_vsl = endpoint_limiter.get_limiter_cust('vsl')
route = '/vsl'


@router.get(
    path=route,
    tags=[tag_name],
    summary='Get locations for the snapshot',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter_vsl.max_request,
                                  limiter_seconds=limiter_vsl.seconds),
    dependencies=[Depends(RateLimiter(interval_seconds=limiter_vsl.seconds,
                                      max_requests=limiter_vsl.max_request))],
    response_model=SuccessfulRequest,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def get_vsls():
    return await get_vsl_handler()


# ------------------------------------------------------------------------------------------------
#             CREATE A VOLUME SNAPSHOT LOCATION
# ------------------------------------------------------------------------------------------------


limiter_create = endpoint_limiter.get_limiter_cust('vsl')
route = '/vsl'


@router.post(
    path=route,
    tags=[tag_name],
    summary='Create a backup storage location',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter_create.max_request,
                                  limiter_seconds=limiter_create.seconds),
    dependencies=[Depends(RateLimiter(interval_seconds=limiter_create.seconds,
                                      max_requests=limiter_create.max_request))],
    response_model=SuccessfulRequest,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_201_CREATED)
@handle_exceptions_endpoint
async def create_vsl(create_bsl: CreateVslRequestSchema):
    return await create_vsl_handler(create_bsl=create_bsl)


# ------------------------------------------------------------------------------------------------
#             DELETE VOLUME SNAPSHOT LOCATION
# ------------------------------------------------------------------------------------------------


limiter_del = endpoint_limiter.get_limiter_cust('vsl')
route = '/vsl'


@router.delete(
    path=route,
    tags=[tag_name],
    summary='Delete storage classes mapping in config map',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter_del.max_request,
                                  limiter_seconds=limiter_del.seconds),
    dependencies=[Depends(RateLimiter(interval_seconds=limiter_del.seconds,
                                      max_requests=limiter_del.max_request))],
    response_model=SuccessfulRequest,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def delete_vsl(vsl: DeleteResourceRequestSchema):
    return await delete_vsl_handler(bsl_delete=vsl.name)

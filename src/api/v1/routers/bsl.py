from fastapi import APIRouter, Depends, status

from constants.response import common_error_authenticated_response

from schemas.request.delete_resource import DeleteResourceRequestSchema
from schemas.response.successful_bsl import SuccessfulBslResponse
from schemas.response.successful_request import SuccessfulRequest
from schemas.request.create_bsl import CreateBslRequestSchema
from schemas.request.default_bsl import DefaultBslRequestSchema

from security.helpers.rate_limiter import RateLimiter, LimiterRequests

from utils.swagger import route_description
from utils.exceptions import handle_exceptions_endpoint

from controllers.bsl import (get_bsls_handler,
                             create_bsl_handler,
                             set_default_bsl_handler,
                             set_remove_default_bsl_handler,
                             delete_bsl_handler)

router = APIRouter()

tag_name = 'Backup Storage Locations'
endpoint_limiter = LimiterRequests(tags=tag_name,
                                   default_key='L1')

# ------------------------------------------------------------------------------------------------
#             GET BACKUP STORAGE LOCATIONS
# ------------------------------------------------------------------------------------------------


limiter_bsl = endpoint_limiter.get_limiter_cust('bsl')
route = '/bsl'


@router.get(
    path=route,
    tags=[tag_name],
    summary='Get list of the backups',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter_bsl.max_request,
                                  limiter_seconds=limiter_bsl.seconds),
    dependencies=[Depends(RateLimiter(interval_seconds=limiter_bsl.seconds,
                                      max_requests=limiter_bsl.max_request))],
    response_model=SuccessfulBslResponse,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def get_bsl():
    return await get_bsls_handler()


# ------------------------------------------------------------------------------------------------
#             CREATE BACKUP STORAGE LOCATION
# ------------------------------------------------------------------------------------------------


limiter_create = endpoint_limiter.get_limiter_cust('bsl')
route = '/bsl'


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
#@handle_exceptions_endpoint
async def create_bsl(bsl: CreateBslRequestSchema):
    return await create_bsl_handler(bsl=bsl)


# ------------------------------------------------------------------------------------------------
#             SET DEFAULT BACKUP STORAGE
# ------------------------------------------------------------------------------------------------


limiter_default = endpoint_limiter.get_limiter_cust('bsl_default')
route = '/bsl/default'


@router.post(
    path=route,
    tags=[tag_name],
    summary='Set default backup storage location',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter_default.max_request,
                                  limiter_seconds=limiter_default.seconds),
    dependencies=[Depends(RateLimiter(interval_seconds=limiter_default.seconds,
                                      max_requests=limiter_default.max_request))],
    response_model=SuccessfulRequest,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_201_CREATED)
@handle_exceptions_endpoint
async def set_default_bsl(default_bsl: DefaultBslRequestSchema):
    if default_bsl.default:
        return await set_default_bsl_handler(default_bsl=default_bsl)
    return await set_remove_default_bsl_handler(default_bsl=default_bsl)


# ------------------------------------------------------------------------------------------------
#             DELETE BACKUP STORAGE LOCATION
# ------------------------------------------------------------------------------------------------


limiter_del = endpoint_limiter.get_limiter_cust('bsl')
route = '/bsl'


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
async def delete_bsl(bsl: DeleteResourceRequestSchema):
    return await delete_bsl_handler(bsl_name=bsl.name)

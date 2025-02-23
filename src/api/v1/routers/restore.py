from fastapi import APIRouter, Depends, status

from configs.response import common_error_authenticated_response
from security.helpers.rate_limiter import RateLimiter, LimiterRequests

from utils.commons import route_description
from utils.handle_exceptions import handle_exceptions_endpoint

from schemas.request.delete_resource import DeleteResourceRequestSchema
from schemas.response.successful_request import SuccessfulRequest
from schemas.response.successful_restores import SuccessfulRestoreResponse
from schemas.request.create_restore import CreateRestoreRequestSchema

from controllers.restore import (get_restores_handler,
                                 create_restore_handler,
                                 delete_restore_handler)
from controllers.common import (get_resource_describe_handler,
                                get_resource_logs_handler)

router = APIRouter()


tag_name = 'Restore'
endpoint_limiter = LimiterRequests(tags=tag_name,
                                   default_key='L1')

# ------------------------------------------------------------------------------------------------
#             GET RESTORES LIST
# ------------------------------------------------------------------------------------------------


limiter_restores = endpoint_limiter.get_limiter_cust("restores")
route = '/restores'


@router.get(
    path=route,
    tags=[tag_name],
    summary='Get restores',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter_restores.max_request,
                                  limiter_seconds=limiter_restores.seconds),
    dependencies=[Depends(RateLimiter(interval_seconds=limiter_restores.seconds,
                                      max_requests=limiter_restores.max_request))],
    response_model=SuccessfulRestoreResponse,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def get_restores(in_progress: bool = False):
    return await get_restores_handler(in_progress=str(in_progress).lower() == 'true')


# ------------------------------------------------------------------------------------------------
#             GET RESTORES LOGS
# ------------------------------------------------------------------------------------------------


limiter_logs = endpoint_limiter.get_limiter_cust('restore_logs')
route = '/restore/logs'


@router.get(
    path=route,
    tags=[tag_name],
    summary='Get logs for restore',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter_logs.max_request,
                                  limiter_seconds=limiter_logs.seconds),
    dependencies=[Depends(RateLimiter(interval_seconds=limiter_logs.seconds,
                                      max_requests=limiter_logs.max_request))],
    response_model=SuccessfulRequest,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def get_restore_logs(resource_name: str):
    return await get_resource_logs_handler(resource_name=resource_name, resource_type='restore')


# ------------------------------------------------------------------------------------------------
#             GET RESTORES DESCRIBE
# ------------------------------------------------------------------------------------------------


limiter_des = endpoint_limiter.get_limiter_cust('restore_describe')
route = '/restore/describe'


@router.get(
    path=route,
    tags=[tag_name],
    summary='Get detail for restore',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter_des.max_request,
                                  limiter_seconds=limiter_des.seconds),
    dependencies=[Depends(RateLimiter(interval_seconds=limiter_des.seconds,
                                      max_requests=limiter_des.max_request))],
    response_model=SuccessfulRequest,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def get_restore_describe(resource_name: str):
    return await get_resource_describe_handler(resource_name=resource_name, resource_type='restore')


# ------------------------------------------------------------------------------------------------
#             DELETE A RESTORE
# ------------------------------------------------------------------------------------------------


limiter_delete = endpoint_limiter.get_limiter_cust('restore')
route = '/restore'


@router.delete(
    path=route,
    tags=[tag_name],
    summary='Delete a restore',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter_delete.max_request,
                                  limiter_seconds=limiter_delete.seconds),
    dependencies=[Depends(RateLimiter(interval_seconds=limiter_delete.seconds,
                                      max_requests=limiter_delete.max_request))],
    response_model=SuccessfulRequest,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def delete_restore(restore: DeleteResourceRequestSchema):
    return await delete_restore_handler(restore_name=restore.name)


# ------------------------------------------------------------------------------------------------
#             CREATE A RESTORE
# ------------------------------------------------------------------------------------------------

limiter_create = endpoint_limiter.get_limiter_cust('restore')
route = '/restore'


@router.post(
    path=route,
    tags=[tag_name],
    summary='Create a new restore',
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
async def create_restore(restore: CreateRestoreRequestSchema):
    return await create_restore_handler(restore)

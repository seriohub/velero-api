from fastapi import APIRouter, Depends, status

from configs.response import common_error_authenticated_response

from security.helpers.rate_limiter import RateLimiter, LimiterRequests

from utils.commons import route_description
from utils.handle_exceptions import handle_exceptions_endpoint

from schemas.response.successful_request import SuccessfulRequest
from schemas.request.storage_class_map import StorageClassMapRequestSchema

from controllers.sc_mapping import (delete_storages_classes_mapping_handler,
                                    update_storages_classes_mapping_handler,
                                    get_storages_classes_map_handler)

router = APIRouter()


tag_name = 'Storage Class Mapping'

endpoint_limiter = LimiterRequests(tags=tag_name,
                                   default_key='L1')

# ------------------------------------------------------------------------------------------------
#             GET STORAGE CLASSES MAPPING
# ------------------------------------------------------------------------------------------------

limiter_sc_mapping = endpoint_limiter.get_limiter_cust('sc_mapping')
route = '/sc-mapping'


@router.get(
    path=route,
    tags=[tag_name],
    summary='Get change storage classes config map',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter_sc_mapping.max_request,
                                  limiter_seconds=limiter_sc_mapping.seconds),
    dependencies=[Depends(RateLimiter(interval_seconds=limiter_sc_mapping.seconds,
                                      max_requests=limiter_sc_mapping.max_request))],
    response_model=SuccessfulRequest,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def get_storages_classes_map():
    return await get_storages_classes_map_handler()


# ------------------------------------------------------------------------------------------------
#             CREATE STORAGE CLASSES MAPPING
# ------------------------------------------------------------------------------------------------

limiter_sc_create = endpoint_limiter.get_limiter_cust('sc_mapping')
route = '/sc-mapping'


@router.post(
    path=route,
    tags=[tag_name],
    summary='Create storage classes config map',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter_sc_create.max_request,
                                  limiter_seconds=limiter_sc_create.seconds),
    dependencies=[Depends(RateLimiter(interval_seconds=limiter_sc_create.seconds,
                                      max_requests=limiter_sc_create.max_request))],
    response_model=SuccessfulRequest,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_201_CREATED)
@handle_exceptions_endpoint
async def create_storages_classes_map(maps: StorageClassMapRequestSchema):
    return await update_storages_classes_mapping_handler(maps=maps)


# ------------------------------------------------------------------------------------------------
#             UPDATE STORAGE CLASSES MAPPING
# ------------------------------------------------------------------------------------------------

limiter_sc_update = endpoint_limiter.get_limiter_cust('sc_mapping')
route = '/sc-mapping'


@router.patch(
    path=route,
    tags=[tag_name],
    summary='Update storage classes config map',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter_sc_update.max_request,
                                  limiter_seconds=limiter_sc_update.seconds),
    dependencies=[Depends(RateLimiter(interval_seconds=limiter_sc_update.seconds,
                                      max_requests=limiter_sc_update.max_request))],
    response_model=SuccessfulRequest,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def update_storages_classes_map(maps: StorageClassMapRequestSchema):
    return await update_storages_classes_mapping_handler(maps=maps)


# ------------------------------------------------------------------------------------------------
#             DELETE STORAGE CLASSES MAPPING
# ------------------------------------------------------------------------------------------------


limiter_sc_delete = endpoint_limiter.get_limiter_cust('sc_mapping')
route = '/sc-mapping'


@router.delete(
    path=route,
    tags=[tag_name],
    summary='Delete storage classes mapping in config map',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter_sc_delete.max_request,
                                  limiter_seconds=limiter_sc_delete.seconds),
    dependencies=[Depends(RateLimiter(interval_seconds=limiter_sc_delete.seconds,
                                      max_requests=limiter_sc_delete.max_request))],
    response_model=SuccessfulRequest,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def delete_storages_classes_map(items: StorageClassMapRequestSchema):
    return await delete_storages_classes_mapping_handler(data_list=items.storageClassMapping)

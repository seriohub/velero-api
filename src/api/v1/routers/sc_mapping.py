from fastapi import APIRouter, Depends, status
from typing import Union
from pydantic import BaseModel

from core.config import ConfigHelper
from security.rate_limiter import RateLimiter, LimiterRequests

from utils.commons import route_description
from utils.handle_exceptions import handle_exceptions_endpoint
from helpers.printer import PrintHelper

from api.common.response_model.failed_request import FailedRequest
from api.common.response_model.successful_request import SuccessfulRequest

from api.v1.controllers.sc_mapping import SCMapping

router = APIRouter()
scMapping = SCMapping()
config_app = ConfigHelper()
print_ls = PrintHelper('[v1.routers.sc_mapping]',
                       level=config_app.get_internal_log_level())

tag_name = 'Storage Class Mapping'

endpoint_limiter = LimiterRequests(printer=print_ls,
                                   tags=tag_name,
                                   default_key='L1')


class StorageClassMap(BaseModel):
    storageClassMapping: dict


limiter_sc_mapping = endpoint_limiter.get_limiter_cust('sc_change_storage_classes_config_map_get')
route = '/sc/change-storage-classes-config-map/get'


@router.get(path=route,
            tags=[tag_name],
            summary='Get change storage classes config map',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter_sc_mapping.max_request,
                                          limiter_seconds=limiter_sc_mapping.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_sc_mapping.seconds,
                                              max_requests=limiter_sc_mapping.max_request))],
            response_model=Union[SuccessfulRequest, FailedRequest],
            status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def get_storages_classes_map():
    return await scMapping.get_storages_classes_map()


limiter_sc_create = endpoint_limiter.get_limiter_cust('sc_change_storage_classes_config_map_create')
route = '/sc/change-storage-classes-config-map/create'


@router.post(path=route,
             tags=[tag_name],
             summary='Create storage classes config map',
             description=route_description(tag=tag_name,
                                           route=route,
                                           limiter_calls=limiter_sc_create.max_request,
                                           limiter_seconds=limiter_sc_create.seconds),
             dependencies=[Depends(RateLimiter(interval_seconds=limiter_sc_create.seconds,
                                               max_requests=limiter_sc_create.max_request))],
             response_model=Union[SuccessfulRequest, FailedRequest],
             status_code=status.HTTP_201_CREATED)
@handle_exceptions_endpoint
async def create_storages_classes_map(items: StorageClassMap):
    return await scMapping.update_storages_classes_mapping(data_list=items.storageClassMapping)


limiter_sc_update = endpoint_limiter.get_limiter_cust('sc_change_storage_classes_config_map_update')
route = '/sc/change-storage-classes-config-map/update'


@router.patch(path=route,
              tags=[tag_name],
              summary='Update storage classes config map',
              description=route_description(tag=tag_name,
                                            route=route,
                                            limiter_calls=limiter_sc_update.max_request,
                                            limiter_seconds=limiter_sc_update.seconds),
              dependencies=[Depends(RateLimiter(interval_seconds=limiter_sc_update.seconds,
                                                max_requests=limiter_sc_update.max_request))],
              response_model=Union[SuccessfulRequest, FailedRequest],
              status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def update_storages_classes_map(items: StorageClassMap):
    return await scMapping.update_storages_classes_mapping(data_list=items.storageClassMapping)


limiter_sc_delete = endpoint_limiter.get_limiter_cust('sc_change_storage_classes_config_map_delete')
route = '/sc/change-storage-classes-config-map/delete'


@router.delete(path=route,
               tags=[tag_name],
               summary='Delete storage classes mapping in config map',
               description=route_description(tag=tag_name,
                                             route=route,
                                             limiter_calls=limiter_sc_delete.max_request,
                                             limiter_seconds=limiter_sc_delete.seconds),
               dependencies=[Depends(RateLimiter(interval_seconds=limiter_sc_delete.seconds,
                                                 max_requests=limiter_sc_delete.max_request))],
               response_model=Union[SuccessfulRequest, FailedRequest],
               status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def delete_storages_classes_map(items: StorageClassMap):
    return await scMapping.delete_storages_classes_mapping(data_list=items.storageClassMapping)

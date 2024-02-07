from fastapi import APIRouter, Depends
from helpers.handle_exceptions import *
from helpers.printer_helper import PrintHelper

from libs.sc_mapping import SCMapping
from libs.security.rate_limiter import RateLimiter, LimiterRequests
from pydantic import BaseModel

router = APIRouter()

scMapping = SCMapping()
print_ls = PrintHelper('routes.k8s_v1')

endpoint_limiter = LimiterRequests(debug=False,
                                   printer=print_ls,
                                   tags='k8s',
                                   default_key='L1')

limiter_sc_mapping = endpoint_limiter.get_limiter_cust('sc_mapping')


class StorageClassMap(BaseModel):
    storageClassMapping: dict


@router.get('/sc/change-storage-classes-config-map/get',
            tags=['Storage Class Mapping'],
            summary='Get change storage classes config map',
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_sc_mapping.seconds,
                                              max_requests=limiter_sc_mapping.max_request))])
@handle_exceptions_async_method
async def get_storages_classes_map():
    return await scMapping.get_storages_classes_map()


@router.post('/sc/change-storage-classes-config-map/create',
             tags=['Storage Class Mapping'],
             summary='Create storage classes config map',
             dependencies=[Depends(RateLimiter(interval_seconds=limiter_sc_mapping.seconds,
                                               max_requests=limiter_sc_mapping.max_request))])
@handle_exceptions_async_method
async def create_storages_classes_map(items: StorageClassMap):
    print(items.storageClassMapping)
    return await scMapping.update_storages_classes_mapping(data_list=items.storageClassMapping)


@router.patch('/sc/change-storage-classes-config-map/update',
              tags=['Storage Class Mapping'],
              summary='Update storage classes config map',
              dependencies=[Depends(RateLimiter(interval_seconds=limiter_sc_mapping.seconds,
                                                max_requests=limiter_sc_mapping.max_request))])
@handle_exceptions_async_method
async def update_storages_classes_map(items: StorageClassMap):
    return await scMapping.update_storages_classes_mapping(data_list=items.storageClassMapping)


@router.delete('/sc/change-storage-classes-config-map/delete',
               tags=['Storage Class Mapping'],
               summary='Delete storage classes mapping in config map',
               dependencies=[Depends(RateLimiter(interval_seconds=limiter_sc_mapping.seconds,
                                                 max_requests=limiter_sc_mapping.max_request))])
@handle_exceptions_async_method
async def set_storages_classes_map(items: StorageClassMap):
    return await scMapping.delete_storages_classes_mapping(data_list=items.storageClassMapping)

from fastapi import APIRouter, Depends, status
from typing import Union

from core.config import ConfigHelper
from security.service.helpers.rate_limiter import RateLimiter, LimiterRequests

from utils.commons import route_description
from utils.handle_exceptions import handle_exceptions_endpoint
from helpers.printer import PrintHelper

from api.common.response_model.failed_request import FailedRequest
from api.common.response_model.successful_request import SuccessfulRequest

from api.v1.controllers.snapshot_location import SnapshotLocation

from api.v1.schemas.create_vsl import CreateVsl
from api.v1.schemas.delete_vsl import DeleteVsl

router = APIRouter()
rate_limiter = RateLimiter()
snapshotLocation = SnapshotLocation()
config_app = ConfigHelper()
print_ls = PrintHelper('[v1.routers.snapshot_location]',
                       level=config_app.get_internal_log_level())


tag_name = 'Volume Snapshot Locations'
endpoint_limiter = LimiterRequests(printer=print_ls,
                                   tags=tag_name,
                                   default_key='L1')


limiter_vsl = endpoint_limiter.get_limiter_cust('vsl')
route = '/vsl'
@router.get(path=route,
            tags=[tag_name],
            summary='Get locations for the snapshot',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter_vsl.max_request,
                                          limiter_seconds=limiter_vsl.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_vsl.seconds,
                                              max_requests=limiter_vsl.max_request))],
            response_model=Union[SuccessfulRequest, FailedRequest],
            status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def get():
    return await snapshotLocation.get()

limiter_create = endpoint_limiter.get_limiter_cust('vsl')
route = '/vsl'
@router.post(path=route,
             tags=[tag_name],
             summary='Create a backup storage location',
             description=route_description(tag=tag_name,
                                           route=route,
                                           limiter_calls=limiter_create.max_request,
                                           limiter_seconds=limiter_create.seconds),
             dependencies=[Depends(RateLimiter(interval_seconds=limiter_create.seconds,
                                               max_requests=limiter_create.max_request))],
             response_model=Union[SuccessfulRequest, FailedRequest],
             status_code=status.HTTP_201_CREATED)
@handle_exceptions_endpoint
async def create(create_bsl: CreateVsl):
    return await snapshotLocation.create(create_bsl=create_bsl)

limiter_del = endpoint_limiter.get_limiter_cust('vsl')
route = '/vsl'
@router.delete(path=route,
               tags=[tag_name],
               summary='Delete storage classes mapping in config map',
               description=route_description(tag=tag_name,
                                             route=route,
                                             limiter_calls=limiter_del.max_request,
                                             limiter_seconds=limiter_del.seconds),
               dependencies=[Depends(RateLimiter(interval_seconds=limiter_del.seconds,
                                                 max_requests=limiter_del.max_request))],
               response_model=Union[SuccessfulRequest, FailedRequest],
               status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def delete_storages_classes_map(bsl_delete: DeleteVsl):
    return await snapshotLocation.delete(bsl_delete=bsl_delete)

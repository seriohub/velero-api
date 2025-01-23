from fastapi import APIRouter, Depends, status
from typing import Union

from core.config import ConfigHelper
from security.service.helpers.rate_limiter import RateLimiter, LimiterRequests

from utils.commons import route_description
from utils.handle_exceptions import handle_exceptions_endpoint
from helpers.printer import PrintHelper

from api.common.response_model.failed_request import FailedRequest
from api.common.response_model.successful_request import SuccessfulRequest

from api.v1.controllers.backup_location import BackupLocation

from api.v1.schemas.create_bsl import CreateBsl
from api.v1.schemas.default_bsl import DefaultBsl
from api.v1.schemas.delete_bsl import DeleteBsl

router = APIRouter()
backupLocation = BackupLocation()
config_app = ConfigHelper()
print_ls = PrintHelper('[v1.routers.backup_location]',
                       level=config_app.get_internal_log_level())


tag_name = 'Backup Storage Locations'
endpoint_limiter = LimiterRequests(printer=print_ls,
                                   tags=tag_name,
                                   default_key='L1')


limiter_bsl = endpoint_limiter.get_limiter_cust('bsl')
route = '/bsl'
@router.get(path=route,
            tags=[tag_name],
            summary='Get list of the backups',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter_bsl.max_request,
                                          limiter_seconds=limiter_bsl.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_bsl.seconds,
                                              max_requests=limiter_bsl.max_request))],
            response_model=Union[SuccessfulRequest, FailedRequest],
            status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def get():
    return await backupLocation.get()


limiter_create = endpoint_limiter.get_limiter_cust('bsl')
route = '/bsl'
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
async def create(create_bsl: CreateBsl):
    return await backupLocation.create(create_bsl=create_bsl)


limiter_default = endpoint_limiter.get_limiter_cust('bsl_default')
route = '/bsl/default'
@router.post(path=route,
             tags=[tag_name],
             summary='Set default backup storage location',
             description=route_description(tag=tag_name,
                                           route=route,
                                           limiter_calls=limiter_default.max_request,
                                           limiter_seconds=limiter_default.seconds),
             dependencies=[Depends(RateLimiter(interval_seconds=limiter_default.seconds,
                                               max_requests=limiter_default.max_request))],
             response_model=Union[SuccessfulRequest, FailedRequest],
             status_code=status.HTTP_201_CREATED)
@handle_exceptions_endpoint
async def set_default_bsl(default_bsl: DefaultBsl):
    if default_bsl.default:
        return await backupLocation.default(default_bsl=default_bsl)
    return await backupLocation.remove_default(default_bsl=default_bsl)


limiter_del = endpoint_limiter.get_limiter_cust('bsl')
route = '/bsl'
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
async def delete_bsl(bsl_delete: DeleteBsl):
    return await backupLocation.delete(bsl_delete=bsl_delete)

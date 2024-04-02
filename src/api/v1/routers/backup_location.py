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

router = APIRouter()
backupLocation = BackupLocation()
config_app = ConfigHelper()
print_ls = PrintHelper('[v1.routers.backup_location]',
                       level=config_app.get_internal_log_level())


tag_name = 'Backup Location'
endpoint_limiter = LimiterRequests(printer=print_ls,
                                   tags=tag_name,
                                   default_key='L1')


limiter = endpoint_limiter.get_limiter_cust('backup_location_get')
route = '/backup-location/get'
@router.get(path=route,
            tags=[tag_name],
            summary='Get list of the backups',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter.max_request,
                                          limiter_seconds=limiter.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter.seconds,
                                              max_requests=limiter.max_request))],
            response_model=Union[SuccessfulRequest, FailedRequest],
            status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def get():
    return await backupLocation.get()

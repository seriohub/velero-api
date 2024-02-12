from fastapi import APIRouter, Depends

from helpers.commons import route_description
from helpers.handle_exceptions import *
from helpers.printer_helper import PrintHelper
from libs.backup_location import BackupLocation

from libs.security.rate_limiter import RateLimiter, LimiterRequests

router = APIRouter()
backupLocation = BackupLocation()
print_ls = PrintHelper('routes.backup_location_v1')
tag_name = 'Backup'
endpoint_limiter = LimiterRequests(debug=False,
                                   printer=print_ls,
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
                                              max_requests=limiter.max_request))]
            )
@handle_exceptions_async_method
async def get():
    return await backupLocation.get()

from fastapi import APIRouter, Depends
from helpers.handle_exceptions import *
from helpers.printer_helper import PrintHelper
from libs.backup_location_v1 import BackupLocationV1

from libs.security.rate_limiter import RateLimiter, LimiterRequests


router = APIRouter()
backupLocation = BackupLocationV1()
print_ls = PrintHelper('routes.backup_location_v1')

endpoint_limiter = LimiterRequests(debug=False,
                                   printer=print_ls,
                                   tags="Backup",
                                   default_key='L1')
limiter = endpoint_limiter.get_limiter_cust("backup_location_get")


@router.get('/backup-location/get',
            tags=["Backup"],
            summary="Get list of the backups",
            dependencies=[Depends(RateLimiter(interval_seconds=limiter.seconds,
                                              max_requests=limiter.max_request))]
            )
@handle_exceptions_async_method
async def get():
    return await backupLocation.get()

from fastapi import APIRouter, Depends
from helpers.handle_exceptions import *
from helpers.printer_helper import PrintHelper

from libs.security.rate_limiter import RateLimiter, LimiterRequests
from libs.snapshot_location_v1 import SnapshotLocationV1

router = APIRouter()
rate_limiter = RateLimiter()
snapshotLocation = SnapshotLocationV1()
print_ls = PrintHelper('routes.snapshot_location_v1')

endpoint_limiter = LimiterRequests(debug=False,
                                   printer=print_ls,
                                   tags="Snapshot",
                                   default_key='L1')
limiter = endpoint_limiter.get_limiter_cust("snapshot_location_get")


@router.get('/snapshot-location/get',
            tags=["Snapshot"],
            summary="Get locations for the snapshot",
            dependencies=[Depends(RateLimiter(interval_seconds=limiter.seconds,
                                              max_requests=limiter.max_request))])
@handle_exceptions_async_method
async def get():
    return await snapshotLocation.get()

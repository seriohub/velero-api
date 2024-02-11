from fastapi import APIRouter, Depends

from helpers.commons import route_description
from helpers.handle_exceptions import *
from helpers.printer_helper import PrintHelper

from libs.security.rate_limiter import RateLimiter, LimiterRequests
from libs.snapshot_location import SnapshotLocation

router = APIRouter()
rate_limiter = RateLimiter()
snapshotLocation = SnapshotLocation()
print_ls = PrintHelper('routes.snapshot_location_v1')
tag_name = 'Snapshot'
endpoint_limiter = LimiterRequests(debug=False,
                                   printer=print_ls,
                                   tags=tag_name,
                                   default_key='L1')
limiter = endpoint_limiter.get_limiter_cust('snapshot_location_get')
route = '/snapshot-location/get'


@router.get(path=route,
            tags=[tag_name],
            summary='Get locations for the snapshot',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter.max_request,
                                          limiter_seconds=limiter.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter.seconds,
                                              max_requests=limiter.max_request))])
@handle_exceptions_async_method
async def get():
    return await snapshotLocation.get()

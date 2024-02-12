from fastapi import APIRouter, Depends

from helpers.commons import route_description
from libs.security.rate_limiter import LimiterRequests
from libs.security.rate_limiter import RateLimiter
from helpers.handle_exceptions import handle_exceptions_async_method
from utils.app_data import __version__, __date__, __app_description__, __app_name__, __admin_email__
from helpers.printer_helper import PrintHelper

print_ls = PrintHelper('routes.info')
router = APIRouter()
tag_name = "Info"
endpoint_limiter = LimiterRequests(debug=False,
                                   printer=print_ls,
                                   tags=tag_name,
                                   default_key='L1')
limiter = endpoint_limiter.get_limiter_cust('info')
route = '/info'


@router.get(path=route,
            tags=[tag_name],
            summary='Get app info',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter.max_request,
                                          limiter_seconds=limiter.seconds),

            dependencies=[Depends(RateLimiter(interval_seconds=limiter.seconds,
                                              max_requests=limiter.max_request))])
@handle_exceptions_async_method
async def info():
    return {
        'data': {
            'app_name': __app_name__,
            'app_description': __app_description__,
            'admin_email': __admin_email__,
            'release_version': f"{__version__}",
            'release_date': f"{__date__}",
        }
    }

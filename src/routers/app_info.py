from fastapi import APIRouter, Depends
from fastapi import Request
from libs.security.rate_limiter import LimiterRequests
from libs.security.rate_limiter import RateLimiter
from helpers.handle_exceptions import handle_exceptions_async_method
from utils.app_data import __version__, __date__, __app_description__, __app_name__, __admin_email__
from helpers.printer_helper import PrintHelper


print_ls = PrintHelper('routes.info')
router = APIRouter()

endpoint_limiter = LimiterRequests(debug=False,
                                   printer=print_ls,
                                   tags="Info",
                                   default_key='L5')
limiter = endpoint_limiter.get_limiter_cust("info")


@router.get("/info",
            tags=["Info"],
            summary="Get app info",
            dependencies=[Depends(RateLimiter(interval_seconds=limiter.seconds,
                                              max_requests=limiter.max_request))])
@handle_exceptions_async_method
async def info(request: Request):
    return {
        "app_name": __app_name__,
        "app_description": __app_description__,
        "admin_email": __admin_email__,
        "release_version": f"release {__version__}",
        "release_date": f"{__date__}",
    }



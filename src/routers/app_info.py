from fastapi import APIRouter, Depends

from helpers.commons import route_description
from libs.security.rate_limiter import LimiterRequests
from libs.security.rate_limiter import RateLimiter
from helpers.handle_exceptions import handle_exceptions_async_method
from utils.app_data import __version__, __date__, __app_description__, __app_name__, __admin_email__
from helpers.printer_helper import PrintHelper
from datetime import datetime
from libs.k8s import K8s
from libs.utils import Utils
from fastapi.responses import JSONResponse


k8s = K8s()
utils = Utils()
router = APIRouter()
print_ls = PrintHelper('[routes.info]')


###


tag_name = "Info"
endpoint_limiter = LimiterRequests(debug=False,
                                   printer=print_ls,
                                   tags=tag_name,
                                   default_key='L1')


limiter = endpoint_limiter.get_limiter_cust('info')
route = '/get'
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
    res = {
        'data': {
            'app_name': __app_name__,
            'app_description': __app_description__,
            'admin_email': __admin_email__,
            'release_version': f"{__version__}",
            'release_date': f"{__date__}",
        }
    }
    return JSONResponse(content=res, status_code=200)


###


endpoint_limiter = LimiterRequests(debug=False,
                                   printer=print_ls,
                                   tags=tag_name,
                                   default_key='L1')
limiter = endpoint_limiter.get_limiter_cust('platform')
route = '/arch'
@router.get(path=route,
            tags=[tag_name],
            summary='Get app identify api architecture',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter.max_request,
                                          limiter_seconds=limiter.seconds),

            dependencies=[Depends(RateLimiter(interval_seconds=limiter.seconds,
                                              max_requests=limiter.max_request))])
@handle_exceptions_async_method
async def identify_architecture():
    return await utils.identify_architecture()


###


tag_name = 'Status'
endpoint_limiter_st = LimiterRequests(debug=False,
                                      printer=print_ls,
                                      tags=tag_name,
                                      default_key='L1')


limiter_status = endpoint_limiter.get_limiter_cust('info_health')
route = '/health'
@router.get(path=route,
            tags=[tag_name],
            summary='UTC time',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter_status.max_request,
                                          limiter_seconds=limiter_status.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_status.seconds,
                                              max_requests=limiter_status.max_request))])
@handle_exceptions_async_method
async def health():
    return {'timestamp': datetime.utcnow()}


limiter_status_h = endpoint_limiter.get_limiter_cust('info_health_k8s')
route = '/health-k8s'
@router.get(path=route,
            tags=[tag_name],
            summary='Get K8s connection an api status',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter_status_h.max_request,
                                          limiter_seconds=limiter_status_h.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_status_h.seconds,
                                              max_requests=limiter_status_h.max_request))])
@handle_exceptions_async_method
async def k8s_nodes_status():
    return await k8s.get_k8s_online()


limiter_origins = endpoint_limiter.get_limiter_cust('info_origins')
route = '/origins'
@router.get(path=route,
            tags=[tag_name],
            summary='Get api origins',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter_status_h.max_request,
                                          limiter_seconds=limiter_status_h.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_status_h.seconds,
                                              max_requests=limiter_status_h.max_request))])
@handle_exceptions_async_method
async def k8s_nodes_status():
    return await utils.get_origins()


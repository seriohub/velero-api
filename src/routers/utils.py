from fastapi import APIRouter, Depends

from helpers.commons import route_description
from helpers.handle_exceptions import *
from helpers.printer_helper import PrintHelper
from libs.k8s import K8s
from libs.security.rate_limiter import RateLimiter, LimiterRequests
from libs.utils import Utils
from datetime import datetime

router = APIRouter()
rate_limiter = RateLimiter()

utils = Utils()
k8s = K8s()

print_ls = PrintHelper('routes.utils_v1')
tag_name = 'Statistics'
endpoint_limiter = LimiterRequests(debug=False,
                                   printer=print_ls,
                                   tags=tag_name,
                                   default_key='L1')
limiter = endpoint_limiter.get_limiter_cust('utilis_stats')
route = '/utils/stats'


@router.get(path=route,
            tags=[tag_name],
            summary='Get backups repository',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter.max_request,
                                          limiter_seconds=limiter.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter.seconds,
                                              max_requests=limiter.max_request))])
@handle_exceptions_async_method
async def stats():
    return await utils.stats()


limiter_v = endpoint_limiter.get_limiter_cust('utilis_version')
route = '/utils/version'


@router.get(path=route,
            tags=[tag_name],
            summary='Get velero client version',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter_v.max_request,
                                          limiter_seconds=limiter_v.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_v.seconds,
                                              max_requests=limiter_v.max_request))])
@handle_exceptions_async_method
async def version():
    return await utils.version()


limiter_inprog = endpoint_limiter.get_limiter_cust('utilis_in_progress')
route = '/utils/in-progress'


@router.get(path=route,
            tags=[tag_name],
            summary='Get operations in progress',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter_inprog.max_request,
                                          limiter_seconds=limiter_inprog.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_inprog.seconds,
                                              max_requests=limiter_inprog.max_request))])
@handle_exceptions_async_method
async def in_progress():
    return await utils.in_progress()


tag_name = 'Status'
endpoint_limiter_st = LimiterRequests(debug=False,
                                      printer=print_ls,
                                      tags=tag_name,
                                      default_key='L1')
limiter_status = endpoint_limiter.get_limiter_cust('utilis_health')
route = '/utils/health'


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


limiter_status_h = endpoint_limiter.get_limiter_cust('utilis_health_k8s')
route = '/utils/health-k8s'


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


tag_name = 'Setup'
endpoint_limiter_setup = LimiterRequests(debug=False,
                                         printer=print_ls,
                                         tags=tag_name,
                                         default_key='L1')

limiter_setup = endpoint_limiter_setup.get_limiter_cust('Setup')
route = '/setup/get-config'


@router.get(path=route,
            tags=[tag_name],
            summary='Get all env variables',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter_setup.max_request,
                                          limiter_seconds=limiter_setup.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_setup.seconds,
                                              max_requests=limiter_setup.max_request))])
@handle_exceptions_async_method
async def app_config():
    return await utils.get_env()

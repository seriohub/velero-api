from fastapi import APIRouter, Depends

from helpers.commons import route_description
from helpers.handle_exceptions import *
from helpers.printer_helper import PrintHelper

from libs.k8s import K8s
from libs.security.rate_limiter import RateLimiter, LimiterRequests


router = APIRouter()
k8s = K8s()
print_ls = PrintHelper('[routes.k8s]')


tag_name = 'k8s'
endpoint_limiter = LimiterRequests(debug=False,
                                   printer=print_ls,
                                   tags=tag_name,
                                   default_key='L1')


limiter = endpoint_limiter.get_limiter_cust('k8s_sc_get')
route = '/k8s/sc/get'
@router.get(path=route,
            tags=[tag_name],
            summary='Get list of storage classes defined in the Kubernetes',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter.max_request,
                                          limiter_seconds=limiter.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter.seconds,
                                              max_requests=limiter.max_request))]
            )
@handle_exceptions_async_method
async def k8s_ns_sc():
    return await k8s.get_k8s_storage_classes()


limiter_a = endpoint_limiter.get_limiter_cust('k8s_ns_get')
route = '/k8s/ns/get'
@router.get(path=route,
            tags=[tag_name],
            summary='Get list of namespaces defined in the Kubernetes',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter_a.max_request,
                                          limiter_seconds=limiter_a.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_a.seconds,
                                              max_requests=limiter_a.max_request))]
            )
@handle_exceptions_async_method
async def k8s_ns_get():
    return await k8s.get_ns()


limiter_cg = endpoint_limiter.get_limiter_cust('k8s_credential_get')
route = '/k8s/credential/get'
@router.get(path=route,
            tags=[tag_name],
            summary='Get credential',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter_cg.max_request,
                                          limiter_seconds=limiter_cg.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_cg.seconds,

                                              max_requests=limiter_cg.max_request))])
@handle_exceptions_async_method
async def get_credential(secret_name=None, secret_key=None):
    return await k8s.get_credential(secret_name, secret_key)


limiter_def_cg = endpoint_limiter.get_limiter_cust('k8s_credential_default_get')
route = '/k8s/credential/default/get'
@router.get(path=route,
            tags=[tag_name],
            summary='Get default credential',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter_def_cg.max_request,
                                          limiter_seconds=limiter_def_cg.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_def_cg.seconds,
                                              max_requests=limiter_def_cg.max_request))])
@handle_exceptions_async_method
async def get_default_credential():
    return await k8s.get_default_credential()

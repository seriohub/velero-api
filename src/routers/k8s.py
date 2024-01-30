from fastapi import APIRouter, Depends
from helpers.handle_exceptions import *
from helpers.printer_helper import PrintHelper

from libs.k8s import K8s
from libs.security.rate_limiter import RateLimiter, LimiterRequests

router = APIRouter()

k8s = K8s()
print_ls = PrintHelper('routes.k8s_v1')

endpoint_limiter = LimiterRequests(debug=False,
                                   printer=print_ls,
                                   tags='k8s',
                                   default_key='L1')

limiter = endpoint_limiter.get_limiter_cust('k8s_sc_get')


@router.get('/k8s/sc/get',
            tags=['K8s'],
            summary='Get list of storage classes defined in the Kubernetes',
            dependencies=[Depends(RateLimiter(interval_seconds=limiter.seconds,
                                              max_requests=limiter.max_request))]
            )
@handle_exceptions_async_method
async def k8s_ns_sc():
    return await k8s.get_k8s_storage_classes()


limiter = endpoint_limiter.get_limiter_cust('k8s_ns_get')


@router.get('/k8s/ns/get',
            tags=['K8s'],
            summary='Get list of namespaces defined in the Kubernetes',
            dependencies=[Depends(RateLimiter(interval_seconds=limiter.seconds,
                                              max_requests=limiter.max_request))]
            )
@handle_exceptions_async_method
async def k8s_ns_get():
    return await k8s.get_ns()


limiter_cg = endpoint_limiter.get_limiter_cust('k8s_credential_get')


@router.get('/k8s/credential/get',
            tags=['K8s'],
            summary='Get credential',
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_cg.seconds,

                                              max_requests=limiter_cg.max_request))])
@handle_exceptions_async_method
async def get_credential(secret_name=None, secret_key=None):
    return await k8s.get_credential(secret_name, secret_key)


limiter_def_cg = endpoint_limiter.get_limiter_cust('k8s_credential_default_get')


@router.get('/k8s/credential/default/get',
            tags=['K8s'],
            summary='Get default credential',
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_def_cg.seconds,
                                              max_requests=limiter_def_cg.max_request))])
@handle_exceptions_async_method
async def get_default_credential():
    return await k8s.get_default_credential()

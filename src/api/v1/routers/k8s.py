from fastapi import APIRouter, Depends, status
from typing import Union

from core.config import ConfigHelper
from security.service.helpers.rate_limiter import RateLimiter, LimiterRequests

from utils.commons import route_description
from utils.handle_exceptions import handle_exceptions_endpoint
from helpers.printer import PrintHelper

from api.common.response_model.failed_request import FailedRequest
from api.common.response_model.successful_request import SuccessfulRequest

from api.v1.controllers.k8s import K8s

router = APIRouter()
k8s = K8s()
config_app = ConfigHelper()
print_ls = PrintHelper('[v1.routers.k8s]',
                       level=config_app.get_internal_log_level())

tag_name = 'K8s'
endpoint_limiter = LimiterRequests(printer=print_ls,
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
                                              max_requests=limiter.max_request))],
            response_model=Union[SuccessfulRequest, FailedRequest],
            status_code=status.HTTP_200_OK
            )
@handle_exceptions_endpoint
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
                                              max_requests=limiter_a.max_request))],
            response_model=Union[SuccessfulRequest, FailedRequest],
            status_code=status.HTTP_200_OK
            )
@handle_exceptions_endpoint
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
                                              max_requests=limiter_cg.max_request))],
            response_model=Union[SuccessfulRequest, FailedRequest],
            status_code=status.HTTP_200_OK
            )
@handle_exceptions_endpoint
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
                                              max_requests=limiter_def_cg.max_request))],
            response_model=Union[SuccessfulRequest, FailedRequest],
            status_code=status.HTTP_200_OK
            )
@handle_exceptions_endpoint
async def get_default_credential():
    return await k8s.get_default_credential()


limiter_logs = endpoint_limiter.get_limiter_cust('k8s_logs')
route = '/k8s/current-pod/logs'


@router.get(path=route,
            tags=[tag_name],
            summary='Get logs for the current pod',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter_logs.max_request,
                                          limiter_seconds=limiter_logs.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_logs.seconds,
                                              max_requests=limiter_logs.max_request))],
            response_model=Union[SuccessfulRequest, FailedRequest],
            status_code=status.HTTP_200_OK
            )
@handle_exceptions_endpoint
async def get_logs(lines: int = 100):
    return await k8s.get_logs(lines=lines)

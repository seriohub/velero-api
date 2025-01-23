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
from api.v1.schemas.create_cloud_credentials import CreateCloudCredentials

router = APIRouter()
k8s = K8s()
config_app = ConfigHelper()
print_ls = PrintHelper('[v1.routers.k8s]',
                       level=config_app.get_internal_log_level())

tag_name = 'K8s'
endpoint_limiter = LimiterRequests(printer=print_ls,
                                   tags=tag_name,
                                   default_key='L1')


limiter_sc = endpoint_limiter.get_limiter_cust('k8s_storage_classes')
route = '/k8s/storage-classes'
@router.get(path=route,
            tags=[tag_name],
            summary='Get list of storage classes defined in the Kubernetes',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter_sc.max_request,
                                          limiter_seconds=limiter_sc.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_sc.seconds,
                                              max_requests=limiter_sc.max_request))],
            response_model=Union[SuccessfulRequest, FailedRequest],
            status_code=status.HTTP_200_OK
            )
@handle_exceptions_endpoint
async def k8s_ns_sc():
    return await k8s.get_k8s_storage_classes()


limiter_ns = endpoint_limiter.get_limiter_cust('k8s_namespaces')
route = '/k8s/namespaces'
@router.get(path=route,
            tags=[tag_name],
            summary='Get list of namespaces defined in the Kubernetes',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter_ns.max_request,
                                          limiter_seconds=limiter_ns.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_ns.seconds,
                                              max_requests=limiter_ns.max_request))],
            response_model=Union[SuccessfulRequest, FailedRequest],
            status_code=status.HTTP_200_OK
            )
@handle_exceptions_endpoint
async def k8s_ns_get():
    return await k8s.get_ns()


limiter_logs = endpoint_limiter.get_limiter_cust('k8s_current_pod_logs')
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


limiter_logs = endpoint_limiter.get_limiter_cust('k8s_velero_secret')
route = '/k8s/velero/secrets'
@router.get(path=route,
            tags=[tag_name],
            summary='Get velero secret',
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
async def get_velero_secret():
    return await k8s.get_velero_secret()

limiter_logs = endpoint_limiter.get_limiter_cust('k8s_velero_secret_key')
route = '/k8s/velero/secret/key'
@router.get(path=route,
            tags=[tag_name],
            summary='Get velero secret\'s key',
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
async def get_velero_secret_key(secret_name):
    return await k8s.get_velero_secret_key(secret_name)

limiter_backups = endpoint_limiter.get_limiter_cust('resource_manifest')
route = '/k8s/velero/manifest'
@router.get(path=route,
            tags=[tag_name],
            summary='Get resource manifest',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter_backups.max_request,
                                          limiter_seconds=limiter_backups.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_backups.seconds,
                                              max_requests=limiter_backups.max_request))],
            response_model=Union[SuccessfulRequest, FailedRequest],
            status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def get_manifest(resource_type: str, resource_name: str):
    return await k8s.get_manifest(resource_type=resource_type, resource_name=resource_name)

tag_name = 'Locations'

limiter_cg = endpoint_limiter.get_limiter_cust('location_credentials')
route = '/location/credentials'
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


limiter_def_cg = endpoint_limiter.get_limiter_cust('location_cloud_credentials')
route = '/location/cloud-credentials'
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


limiter_create_cr = endpoint_limiter.get_limiter_cust('location_create_credentials')
route = '/location/create-credentials'
@router.post(path=route,
             tags=[tag_name],
             summary='Send report',
             description=route_description(tag=tag_name,
                                           route=route,
                                           limiter_calls=limiter_create_cr.max_request,
                                           limiter_seconds=limiter_create_cr.seconds),
             dependencies=[Depends(RateLimiter(interval_seconds=limiter_create_cr.seconds,
                                               max_requests=limiter_create_cr.max_request))],
             response_model=Union[SuccessfulRequest, FailedRequest],
             status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def create_credentials(cloud_credentials: CreateCloudCredentials):
    return await k8s.create_cloud_credentials(cloud_credentials=cloud_credentials)



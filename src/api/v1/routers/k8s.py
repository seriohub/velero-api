from fastapi import APIRouter, Depends, status

from constants.response import common_error_authenticated_response

from security.helpers.rate_limiter import RateLimiter, LimiterRequests

from utils.swagger import route_description
from utils.exceptions import handle_exceptions_endpoint

from schemas.response.successful_request import SuccessfulRequest

from controllers.k8s import (get_k8s_storage_classes_handler,
                             get_ns_handler,
                             get_logs_handler,
                             get_manifest_handler)

router = APIRouter()

tag_name = 'Kubernetes'
endpoint_limiter = LimiterRequests(tags=tag_name,
                                   default_key='L1')

# ------------------------------------------------------------------------------------------------
#             GET K8S STORAGE CLASSES
# ------------------------------------------------------------------------------------------------


limiter_sc = endpoint_limiter.get_limiter_cust('k8s_storage_classes')
route = '/k8s/storage-classes'


@router.get(
    path=route,
    tags=[tag_name],
    summary='Get list of storage classes defined in the Kubernetes',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter_sc.max_request,
                                  limiter_seconds=limiter_sc.seconds),
    dependencies=[Depends(RateLimiter(interval_seconds=limiter_sc.seconds,
                                      max_requests=limiter_sc.max_request))],
    response_model=SuccessfulRequest,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_200_OK
)
@handle_exceptions_endpoint
async def get_storage_classes():
    return await get_k8s_storage_classes_handler()


# ------------------------------------------------------------------------------------------------
#             GET K8S NAMESPACES
# ------------------------------------------------------------------------------------------------


limiter_ns = endpoint_limiter.get_limiter_cust('k8s_namespaces')
route = '/k8s/namespaces'


@router.get(
    path=route,
    tags=[tag_name],
    summary='Get list of namespaces defined in the Kubernetes',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter_ns.max_request,
                                  limiter_seconds=limiter_ns.seconds),
    dependencies=[Depends(RateLimiter(interval_seconds=limiter_ns.seconds,
                                      max_requests=limiter_ns.max_request))],
    response_model=SuccessfulRequest,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_200_OK
)
@handle_exceptions_endpoint
async def get_namespaces():
    return await get_ns_handler()


# ------------------------------------------------------------------------------------------------
#             GET K8S POD LOGS
# ------------------------------------------------------------------------------------------------


limiter_logs = endpoint_limiter.get_limiter_cust('k8s_current_pod_logs')
route = '/k8s/current-pod/logs'


@router.get(
    path=route,
    tags=[tag_name],
    summary='Get logs for the current pod',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter_logs.max_request,
                                  limiter_seconds=limiter_logs.seconds),
    dependencies=[Depends(RateLimiter(interval_seconds=limiter_logs.seconds,
                                      max_requests=limiter_logs.max_request))],
    response_model=SuccessfulRequest,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_200_OK
)
@handle_exceptions_endpoint
async def get_pod_logs(lines: int = 100):
    return await get_logs_handler(lines=lines)


# ------------------------------------------------------------------------------------------------
#             GET VELERO MANIFEST
# ------------------------------------------------------------------------------------------------


limiter_backups = endpoint_limiter.get_limiter_cust('resource_manifest')
route = '/k8s/velero/manifest'


@router.get(
    path=route,
    tags=[tag_name],
    summary='Get resource manifest',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter_backups.max_request,
                                  limiter_seconds=limiter_backups.seconds),
    dependencies=[Depends(RateLimiter(interval_seconds=limiter_backups.seconds,
                                      max_requests=limiter_backups.max_request))],
    response_model=SuccessfulRequest,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def get_manifest(resource_type: str, resource_name: str):
    return await get_manifest_handler(resource_type=resource_type, resource_name=resource_name)

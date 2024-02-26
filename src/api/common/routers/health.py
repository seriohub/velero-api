from fastapi import APIRouter, Depends, status

from datetime import datetime
from typing import Union

from utils.commons import route_description
from utils.handle_exceptions import handle_exceptions_endpoint
from helpers.printer import PrintHelper

from security.rate_limiter import LimiterRequests
from security.rate_limiter import RateLimiter

from api.common.response_model.failed_request import FailedRequest
from api.common.response_model.successful_request import SuccessfulRequest

from api.common.controllers.health import Health


router = APIRouter()

health = Health()

print_ls = PrintHelper('[common.routers.health]')


tag_name = 'health'

endpoint_limiter = LimiterRequests(debug=False,
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
                                              max_requests=limiter_status.max_request))],
            response_model=dict,
            status_code=status.HTTP_200_OK
            )
@handle_exceptions_endpoint
async def get_health() -> dict:
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
                                              max_requests=limiter_status_h.max_request))],
            response_model=Union[SuccessfulRequest, FailedRequest],
            status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def get_k8s_nodes_status():
    return await health.get_k8s_online()

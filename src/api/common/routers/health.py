from fastapi import APIRouter, Depends, status

from datetime import datetime
from typing import Union

from core.config import ConfigHelper
from utils.commons import route_description
from utils.handle_exceptions import handle_exceptions_endpoint

from security.service.helpers.rate_limiter import LimiterRequests
from security.service.helpers.rate_limiter import RateLimiter

from api.common.response_model.failed_request import FailedRequest
from api.common.response_model.successful_request import SuccessfulRequest

from api.common.controllers.health import Health

router = APIRouter()

health = Health()
config_app = ConfigHelper()

tag_name = 'Health'

endpoint_limiter = LimiterRequests(tags=tag_name,
                                   default_key='L1')

limiter_utc = endpoint_limiter.get_limiter_cust('health_utc')
route = '/utc'


@router.get(path=route,
            tags=[tag_name],
            summary='UTC time',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter_utc.max_request,
                                          limiter_seconds=limiter_utc.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_utc.seconds,
                                              max_requests=limiter_utc.max_request))],
            response_model=dict,
            status_code=status.HTTP_200_OK
            )
@handle_exceptions_endpoint
async def get_health() -> dict:
    return {'timestamp': datetime.utcnow().strftime('%B %d %Y - %H:%M:%S')}


limiter_k8s = endpoint_limiter.get_limiter_cust('health_k8s')
route = '/k8s'


@router.get(path=route,
            tags=[tag_name],
            summary='Get K8s connection an api status',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter_k8s.max_request,
                                          limiter_seconds=limiter_k8s.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_k8s.seconds,
                                              max_requests=limiter_k8s.max_request))],
            response_model=Union[SuccessfulRequest, FailedRequest],
            status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def get_k8s_nodes_status():
    return await health.get_k8s_online()

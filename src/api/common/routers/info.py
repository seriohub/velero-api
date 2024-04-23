from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from typing import Union

from requests import Session

from core.config import ConfigHelper
from security.helpers.database import get_db
from utils.commons import route_description
from utils.handle_exceptions import handle_exceptions_endpoint
from helpers.printer import PrintHelper
from app_data import __version__, __date__, __app_description__, __app_name__, __admin_email__

from security.service.helpers.rate_limiter import LimiterRequests
from security.service.helpers.rate_limiter import RateLimiter

from api.common.response_model.failed_request import FailedRequest
from api.common.response_model.successful_request import SuccessfulRequest

from api.common.controllers.info import Info
from service.watchdog_service import WatchdogService

router = APIRouter()

info = Info()
watchdogService = WatchdogService()

config_app = ConfigHelper()
print_ls = PrintHelper('[common.routers.info]',
                       level=config_app.get_internal_log_level())

tag_name = "Info"

endpoint_limiter = LimiterRequests(printer=print_ls,
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
                                              max_requests=limiter.max_request))],
            response_model=Union[SuccessfulRequest, FailedRequest],
            status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def get_app_info():
    watchdog_release = await watchdogService.version()
    res = {'app_name': __app_name__,
           'app_description': __app_description__,
           'admin_email': __admin_email__,
           'release_version': f"{__version__}",
           'release_date': f"{__date__}"
           }
    if watchdog_release['success']:
        res['watchdog_release_version'] = watchdog_release['data']['release_version']
        res['watchdog_release_date'] = watchdog_release['data']['release_date']
    response = SuccessfulRequest(payload=res)
    return JSONResponse(content=response.toJSON(), status_code=200)


endpoint_limiter = LimiterRequests(printer=print_ls,
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
                                              max_requests=limiter.max_request))],
            response_model=Union[SuccessfulRequest, FailedRequest],
            status_code=status.HTTP_200_OK
            )
@handle_exceptions_endpoint
async def get_architecture():
    return await info.identify_architecture()


limiter_origins = endpoint_limiter.get_limiter_cust('info_origins')
route = '/origins'


@router.get(path=route,
            tags=[tag_name],
            summary='Get api origins',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter_origins.max_request,
                                          limiter_seconds=limiter_origins.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_origins.seconds,
                                              max_requests=limiter_origins.max_request))],
            response_model=Union[SuccessfulRequest, FailedRequest],
            status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def k8s_nodes_status():
    return await info.get_origins()


limiter_origins = endpoint_limiter.get_limiter_cust('info_watchdog')

route = '/watchdog'


@router.get(path=route,
            tags=[tag_name],
            summary='Get info watchdog',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter_origins.max_request,
                                          limiter_seconds=limiter_origins.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_origins.seconds,
                                              max_requests=limiter_origins.max_request))],
            response_model=Union[SuccessfulRequest, FailedRequest],
            status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def watchdog_config():
    return await info.watchdog_online()


limiter_origins = endpoint_limiter.get_limiter_cust('info_get_repo_tags')
route = '/get-repo-tags'


@router.get(path=route,
            tags=[tag_name],
            summary='Get the latest tag from GitHub for projects affected by velero-api',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter_origins.max_request,
                                          limiter_seconds=limiter_origins.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_origins.seconds,
                                              max_requests=limiter_origins.max_request))],
            response_model=Union[SuccessfulRequest, FailedRequest],
            status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def watchdog_config(db: Session = Depends(get_db)):
    return await info.last_tags_from_github(db)

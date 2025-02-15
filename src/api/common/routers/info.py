from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from typing import Union

from requests import Session

from core.config import ConfigHelper
from helpers.database.database import get_db
from utils.commons import route_description
from utils.handle_exceptions import handle_exceptions_endpoint

from app_data import (__version__,
                      __date__,
                      __app_description__,
                      __app_name__,
                      __admin_email__,
                      __helm_version__,
                      __helm_app_version__,
                      __helm_api__,
                      __helm_ui__,
                      __helm_watchdog__)

from security.helpers.rate_limiter import LimiterRequests
from security.helpers.rate_limiter import RateLimiter

from api.common.response_model.failed_request import FailedRequest
from api.common.response_model.successful_request import SuccessfulRequest

from api.common.controllers.info import Info
from service.watchdog_service import WatchdogService

router = APIRouter()

info = Info()
watchdogService = WatchdogService()

config_app = ConfigHelper()

tag_name = "Info"

endpoint_limiter = LimiterRequests(tags=tag_name,
                                   default_key='L1')

limiter_app = endpoint_limiter.get_limiter_cust('info_app')
route = '/app'


@router.get(path=route,
            tags=[tag_name],
            summary='Get app info',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter_app.max_request,
                                          limiter_seconds=limiter_app.seconds),

            dependencies=[Depends(RateLimiter(interval_seconds=limiter_app.seconds,
                                              max_requests=limiter_app.max_request))],
            response_model=Union[SuccessfulRequest, FailedRequest],
            status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def get_app_info():
    watchdog_release = await watchdogService.version()
    res = {'app_name': __app_name__,
           'app_description': __app_description__,
           'admin_email': __admin_email__,
           'helm_version': f'{__helm_version__}',
           'helm_app_version': f'{__helm_app_version__}',
           'helm_api': f'{__helm_api__}',
           'helm_ui': f'{__helm_ui__}',
           'helm_watchdog': f'{__helm_watchdog__}',
           'auth_enabled': f'{config_app.get_auth_enabled()}',
           'auth_type': f'{config_app.get_auth_type()}',
           'api_release_version': f'{__version__}',
           'api_release_date': f'{__date__}',
           }
    if watchdog_release['success']:
        res['watchdog_release_version'] = watchdog_release['data']['release_version']
        res['watchdog_release_date'] = watchdog_release['data']['release_date']
    response = SuccessfulRequest(payload=res)
    return JSONResponse(content=response.toJSON(), status_code=200)


limiter_arch = endpoint_limiter.get_limiter_cust('info_arch')
route = '/arch'


@router.get(path=route,
            tags=[tag_name],
            summary='Get app identify api architecture',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter_arch.max_request,
                                          limiter_seconds=limiter_arch.seconds),

            dependencies=[Depends(RateLimiter(interval_seconds=limiter_arch.seconds,
                                              max_requests=limiter_arch.max_request))],
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
async def k8s_nodes_origins():
    return await info.get_origins()


limiter_comp = endpoint_limiter.get_limiter_cust('info_compatibility_table')
route = '/compatibility-table'


@router.get(path=route,
            tags=[tag_name],
            summary='Obtain compatibility of the user interface version with the other components of the project.',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter_comp.max_request,
                                          limiter_seconds=limiter_comp.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_comp.seconds,
                                              max_requests=limiter_comp.max_request))],
            response_model=Union[SuccessfulRequest, FailedRequest],
            status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def ui_compatibility(version: str):
    return await info.ui_compatibility(version)


tag_name = "Info software versions"

limiter_vui_repo_tags = endpoint_limiter.get_limiter_cust('info_vui_repo_tags')
route = '/vui-repo-tags'


@router.get(path=route,
            tags=[tag_name],
            summary='Get the latest tag from GitHub for vui projects',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter_vui_repo_tags.max_request,
                                          limiter_seconds=limiter_vui_repo_tags.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_vui_repo_tags.seconds,
                                              max_requests=limiter_vui_repo_tags.max_request))],
            response_model=Union[SuccessfulRequest, FailedRequest],
            status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def repository_tags(force_scrapy: bool = False, db: Session = Depends(get_db)):
    return await info.last_tags_from_github(force_refresh=force_scrapy,
                                            db=db)


limiter_velero_repo_tags = endpoint_limiter.get_limiter_cust('info_velero_repo_tag')
route = '/velero-repo-tag'


@router.get(path=route,
            tags=[tag_name],
            summary='Get the latest tag from GitHub for Velero project',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter_velero_repo_tags.max_request,
                                          limiter_seconds=limiter_velero_repo_tags.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_velero_repo_tags.seconds,
                                              max_requests=limiter_velero_repo_tags.max_request))],
            response_model=Union[SuccessfulRequest, FailedRequest],
            status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def repository_velero_tag(force_scrapy: bool = False, db: Session = Depends(get_db)):
    return await info.last_tag_velero_from_github(force_refresh=force_scrapy,
                                                  db=db)

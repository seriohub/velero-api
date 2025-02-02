from fastapi import APIRouter, status, Depends
from typing import Union

from core.config import ConfigHelper
from security.service.helpers.rate_limiter import RateLimiter, LimiterRequests

from utils.commons import route_description
from utils.handle_exceptions import handle_exceptions_endpoint

from api.common.response_model.failed_request import FailedRequest
from api.common.response_model.successful_request import SuccessfulRequest

from api.v1.controllers.watchdog import Watchdog
from api.v1.schemas.apprise_test_service import AppriseTestService
from api.v1.schemas.create_user_service import CreateUserService
from api.v1.schemas.delete_user_service import DeleteUserService
from api.v1.schemas.update_user_config import UpdateUserConfig

router = APIRouter()
rate_limiter = RateLimiter()
watchdog = Watchdog()
config_app = ConfigHelper()

tag_name = 'Watchdog'

endpoint_limiter_setup = LimiterRequests(tags=tag_name,
                                         default_key='L1')
limiter_setup = endpoint_limiter_setup.get_limiter_cust('watchdog_info')
route = '/watchdog/info'


@router.get(path=route,
            tags=[tag_name],
            summary='Get info watchdog',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter_setup.max_request,
                                          limiter_seconds=limiter_setup.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_setup.seconds,
                                              max_requests=limiter_setup.max_request))],
            response_model=Union[SuccessfulRequest, FailedRequest],
            status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def watchdog_config():
    return await watchdog.version()


limiter_v = endpoint_limiter_setup.get_limiter_cust('watchdog_send_report')
route = '/watchdog/send-report'


@router.post(path=route,
             tags=[tag_name],
             summary='Send report',
             description=route_description(tag=tag_name,
                                           route=route,
                                           limiter_calls=limiter_v.max_request,
                                           limiter_seconds=limiter_v.seconds),
             dependencies=[Depends(RateLimiter(interval_seconds=limiter_v.seconds,
                                               max_requests=limiter_v.max_request))],
             response_model=Union[SuccessfulRequest, FailedRequest],
             status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def send_report():
    return await watchdog.send_report()


limiter_setup = endpoint_limiter_setup.get_limiter_cust('watchdog_environment')
route = '/watchdog/environment'


@router.get(path=route,
            tags=[tag_name],
            summary='Get all env variables',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter_setup.max_request,
                                          limiter_seconds=limiter_setup.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_setup.seconds,
                                              max_requests=limiter_setup.max_request))],
            response_model=Union[SuccessfulRequest, FailedRequest],
            status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def watchdog_environment():
    return await watchdog.get_env()


limiter_setup = endpoint_limiter_setup.get_limiter_cust('watchdog_cron')
route = '/watchdog/cron'


@router.get(path=route,
            tags=[tag_name],
            summary='Get cron',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter_setup.max_request,
                                          limiter_seconds=limiter_setup.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_setup.seconds,
                                              max_requests=limiter_setup.max_request))],
            response_model=Union[SuccessfulRequest, FailedRequest],
            status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def app_config():
    return await watchdog.get_cron()


limiter_v = endpoint_limiter_setup.get_limiter_cust('watchdog_test_service')
route = '/watchdog/test-service'


@router.post(path=route,
             tags=[tag_name],
             summary='Send a test message to verify channel settings',
             description=route_description(tag=tag_name,
                                           route=route,
                                           limiter_calls=limiter_v.max_request,
                                           limiter_seconds=limiter_v.seconds),
             dependencies=[Depends(RateLimiter(interval_seconds=limiter_v.seconds,
                                               max_requests=limiter_v.max_request))],
             response_model=Union[SuccessfulRequest, FailedRequest],
             status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def send_test_notification(provider: AppriseTestService):
    return await watchdog.send_test_notification(provider)


limiter_v = endpoint_limiter_setup.get_limiter_cust('watchdog_restart')
route = '/watchdog/restart'


@router.post(path=route,
             tags=[tag_name],
             summary='Force restart watchdog app',
             description=route_description(tag=tag_name,
                                           route=route,
                                           limiter_calls=limiter_v.max_request,
                                           limiter_seconds=limiter_v.seconds),
             dependencies=[Depends(RateLimiter(interval_seconds=limiter_v.seconds,
                                               max_requests=limiter_v.max_request))],
             response_model=Union[SuccessfulRequest, FailedRequest],
             status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def restart():
    return await watchdog.restart()


limiter_setup = endpoint_limiter_setup.get_limiter_cust('watchdog_user_configs')
route = '/watchdog/user/configs'


@router.get(path=route,
            tags=[tag_name],
            summary='Get watchdog user configs',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter_setup.max_request,
                                          limiter_seconds=limiter_setup.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_setup.seconds,
                                              max_requests=limiter_setup.max_request))],
            response_model=Union[SuccessfulRequest, FailedRequest],
            status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def user_config():
    return await watchdog.user_configs()


limiter_setup = endpoint_limiter_setup.get_limiter_cust('watchdog_user_configs')
route = '/watchdog/user/configs'


@router.put(path=route,
            tags=[tag_name],
            summary='Update watchdog user configs',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter_setup.max_request,
                                          limiter_seconds=limiter_setup.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_setup.seconds,
                                              max_requests=limiter_setup.max_request))],
            response_model=Union[SuccessfulRequest, FailedRequest],
            status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def update_user_config(user_configs: UpdateUserConfig):
    return await watchdog.update_user_configs(user_configs)


limiter_setup = endpoint_limiter_setup.get_limiter_cust('watchdog_user_secrets')
route = '/watchdog/user/services'


@router.get(path=route,
            tags=[tag_name],
            summary='Get watchdog services',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter_setup.max_request,
                                          limiter_seconds=limiter_setup.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_setup.seconds,
                                              max_requests=limiter_setup.max_request))],
            response_model=Union[SuccessfulRequest, FailedRequest],
            status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def user_services():
    return await watchdog.user_services()


limiter_setup = endpoint_limiter_setup.get_limiter_cust('watchdog_user_service')
route = '/watchdog/user/service'


@router.post(path=route,
             tags=[tag_name],
             summary='Create watchdog user service',
             description=route_description(tag=tag_name,
                                           route=route,
                                           limiter_calls=limiter_setup.max_request,
                                           limiter_seconds=limiter_setup.seconds),
             dependencies=[Depends(RateLimiter(interval_seconds=limiter_setup.seconds,
                                               max_requests=limiter_setup.max_request))],
             response_model=Union[SuccessfulRequest, FailedRequest],
             status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def create_user_services(service: CreateUserService):
    return await watchdog.create_user_services(service)


limiter_setup = endpoint_limiter_setup.get_limiter_cust('watchdog_user_service')
route = '/watchdog/user/service'


@router.delete(path=route,
               tags=[tag_name],
               summary='Delete watchdog user service',
               description=route_description(tag=tag_name,
                                             route=route,
                                             limiter_calls=limiter_setup.max_request,
                                             limiter_seconds=limiter_setup.seconds),
               dependencies=[Depends(RateLimiter(interval_seconds=limiter_setup.seconds,
                                                 max_requests=limiter_setup.max_request))],
               response_model=Union[SuccessfulRequest, FailedRequest],
               status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def delete_user_services(service: DeleteUserService):
    return await watchdog.delete_user_services(service)

from fastapi import APIRouter, status, Depends

from constants.response import common_error_authenticated_response

from controllers.setup import get_env_handler

from security.helpers.rate_limiter import RateLimiter, LimiterRequests

from utils.swagger import route_description
from utils.exceptions import handle_exceptions_endpoint

from schemas.request.delete_resource import DeleteResourceRequestSchema
from schemas.response.successful_request import SuccessfulRequest
from schemas.request.apprise_test_service import AppriseTestServiceRequestSchema
from schemas.request.create_user_service import CreateUserServiceRequestSchema
from schemas.request.update_user_config import UpdateUserConfigRequestSchema

from controllers.watchdog import (version_handler,
                                  send_test_notification_handler,
                                  get_apprise_services_handler,
                                  update_user_configs_handler,
                                  user_configs_handler,
                                  restart_handler,
                                  get_cron_handler,
                                  send_report_handler,
                                  create_apprise_service_handler,
                                  delete_apprise_service_handler)

router = APIRouter()
rate_limiter = RateLimiter()



tag_name = 'Watchdog'

endpoint_limiter_setup = LimiterRequests(tags=tag_name,
                                         default_key='L1')

# ------------------------------------------------------------------------------------------------
#             GET WATCHDOG INFO
# ------------------------------------------------------------------------------------------------


limiter_setup = endpoint_limiter_setup.get_limiter_cust('watchdog_info')
route = '/watchdog/info'


@router.get(
    path=route,
    tags=[tag_name],
    summary='Get info watchdog',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter_setup.max_request,
                                  limiter_seconds=limiter_setup.seconds),
    dependencies=[Depends(RateLimiter(interval_seconds=limiter_setup.seconds,
                                      max_requests=limiter_setup.max_request))],
    response_model=SuccessfulRequest,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def watchdog_config():
    return await version_handler()


# ------------------------------------------------------------------------------------------------
#             WATCHDOG SEND REPORT
# ------------------------------------------------------------------------------------------------

limiter_v = endpoint_limiter_setup.get_limiter_cust('watchdog_send_report')
route = '/watchdog/send-report'


@router.post(
    path=route,
    tags=[tag_name],
    summary='Send report',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter_v.max_request,
                                  limiter_seconds=limiter_v.seconds),
    dependencies=[Depends(RateLimiter(interval_seconds=limiter_v.seconds,
                                      max_requests=limiter_v.max_request))],
    response_model=SuccessfulRequest,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def send_watchdog_report():
    return await send_report_handler()


# ------------------------------------------------------------------------------------------------
#             GET WATCHDOG ENVIRONMENT
# ------------------------------------------------------------------------------------------------


limiter_setup = endpoint_limiter_setup.get_limiter_cust('watchdog_environment')
route = '/watchdog/environment'


@router.get(
    path=route,
    tags=[tag_name],
    summary='Get all env variables',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter_setup.max_request,
                                  limiter_seconds=limiter_setup.seconds),
    dependencies=[Depends(RateLimiter(interval_seconds=limiter_setup.seconds,
                                      max_requests=limiter_setup.max_request))],
    response_model=SuccessfulRequest,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def get_watchdog_environment():
    return await get_env_handler()


# ------------------------------------------------------------------------------------------------
#             GET WATCHDOG CRONJOB INFO
# ------------------------------------------------------------------------------------------------


limiter_setup = endpoint_limiter_setup.get_limiter_cust('watchdog_cron')
route = '/watchdog/cron'


@router.get(
    path=route,
    tags=[tag_name],
    summary='Get cron',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter_setup.max_request,
                                  limiter_seconds=limiter_setup.seconds),
    dependencies=[Depends(RateLimiter(interval_seconds=limiter_setup.seconds,
                                      max_requests=limiter_setup.max_request))],
    response_model=SuccessfulRequest,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def get_watchdog_cron():
    return await get_cron_handler()


# ------------------------------------------------------------------------------------------------
#             RESTART WATCHDOG POD
# ------------------------------------------------------------------------------------------------


limiter_v = endpoint_limiter_setup.get_limiter_cust('watchdog_restart')
route = '/watchdog/restart'


@router.post(
    path=route,
    tags=[tag_name],
    summary='Force restart watchdog app',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter_v.max_request,
                                  limiter_seconds=limiter_v.seconds),
    dependencies=[Depends(RateLimiter(interval_seconds=limiter_v.seconds,
                                      max_requests=limiter_v.max_request))],
    response_model=SuccessfulRequest,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def watchdog_restart():
    return await restart_handler()


# ------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------
#             USER CONFIGS
# ------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------


# ------------------------------------------------------------------------------------------------
#             GET WATCHDOG USER CONFIGS
# ------------------------------------------------------------------------------------------------


limiter_setup = endpoint_limiter_setup.get_limiter_cust('watchdog_user_configs')
route = '/watchdog/user/configs'


@router.get(
    path=route,
    tags=[tag_name],
    summary='Get watchdog user configs',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter_setup.max_request,
                                  limiter_seconds=limiter_setup.seconds),
    dependencies=[Depends(RateLimiter(interval_seconds=limiter_setup.seconds,
                                      max_requests=limiter_setup.max_request))],
    response_model=SuccessfulRequest,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def get_user_watchdog_config():
    return await user_configs_handler()


# ------------------------------------------------------------------------------------------------
#             UPDATE USER WATCHDOG CONFIGS
# ------------------------------------------------------------------------------------------------


limiter_setup = endpoint_limiter_setup.get_limiter_cust('watchdog_user_configs')
route = '/watchdog/user/configs'


@router.put(
    path=route,
    tags=[tag_name],
    summary='Update watchdog user configs',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter_setup.max_request,
                                  limiter_seconds=limiter_setup.seconds),
    dependencies=[Depends(RateLimiter(interval_seconds=limiter_setup.seconds,
                                      max_requests=limiter_setup.max_request))],
    response_model=SuccessfulRequest,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def update_user_watchdog_config(user_configs: UpdateUserConfigRequestSchema):
    return await update_user_configs_handler(user_configs)


# ------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------
#             APPRISE
# ------------------------------------------------------------------------------------------------#
# ------------------------------------------------------------------------------------------------


# ------------------------------------------------------------------------------------------------
#             GET APPRISE SERVICES
# ------------------------------------------------------------------------------------------------


limiter_setup = endpoint_limiter_setup.get_limiter_cust('watchdog_user_secrets')
route = '/watchdog/user/services'


@router.get(
    path=route,
    tags=[tag_name],
    summary='Get watchdog services',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter_setup.max_request,
                                  limiter_seconds=limiter_setup.seconds),
    dependencies=[Depends(RateLimiter(interval_seconds=limiter_setup.seconds,
                                      max_requests=limiter_setup.max_request))],
    response_model=SuccessfulRequest,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def get_apprise_services():
    return await get_apprise_services_handler()


# ------------------------------------------------------------------------------------------------
#             CREATE APPRISE SERVICE
# ------------------------------------------------------------------------------------------------


limiter_setup = endpoint_limiter_setup.get_limiter_cust('watchdog_user_service')
route = '/watchdog/user/service'


@router.post(
    path=route,
    tags=[tag_name],
    summary='Create watchdog user service',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter_setup.max_request,
                                  limiter_seconds=limiter_setup.seconds),
    dependencies=[Depends(RateLimiter(interval_seconds=limiter_setup.seconds,
                                      max_requests=limiter_setup.max_request))],
    response_model=SuccessfulRequest,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def create_apprise_services(service: CreateUserServiceRequestSchema):
    return await create_apprise_service_handler(service)


# ------------------------------------------------------------------------------------------------
#             DELETE APPRISE SERVICE
# ------------------------------------------------------------------------------------------------


limiter_setup = endpoint_limiter_setup.get_limiter_cust('watchdog_user_service')
route = '/watchdog/user/service'


@router.delete(
    path=route,
    tags=[tag_name],
    summary='Delete watchdog user service',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter_setup.max_request,
                                  limiter_seconds=limiter_setup.seconds),
    dependencies=[Depends(RateLimiter(interval_seconds=limiter_setup.seconds,
                                      max_requests=limiter_setup.max_request))],
    response_model=SuccessfulRequest,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def delete_apprise_service(service: DeleteResourceRequestSchema):
    return await delete_apprise_service_handler(service.name)


# ------------------------------------------------------------------------------------------------
#             TEST APPRISE SERVICE
# ------------------------------------------------------------------------------------------------


limiter_v = endpoint_limiter_setup.get_limiter_cust('watchdog_test_service')
route = '/watchdog/test-service'


@router.post(
    path=route,
    tags=[tag_name],
    summary='Send a test message to verify channel settings',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter_v.max_request,
                                  limiter_seconds=limiter_v.seconds),
    dependencies=[Depends(RateLimiter(interval_seconds=limiter_v.seconds,
                                      max_requests=limiter_v.max_request))],
    response_model=SuccessfulRequest,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def send_apprise_test_notification(provider: AppriseTestServiceRequestSchema):
    return await send_test_notification_handler(provider)

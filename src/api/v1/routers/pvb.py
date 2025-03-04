from fastapi import APIRouter, status, Depends

from constants.response import common_error_authenticated_response

from security.helpers.rate_limiter import RateLimiter, LimiterRequests

from utils.swagger import route_description
from utils.exceptions import handle_exceptions_endpoint

from schemas.response.successful_request import SuccessfulRequest

from controllers.pvb import (get_pod_volume_backups_handler,
                             get_pod_volume_backup_details_handler)

router = APIRouter()

tag_name = "Pod Volume Backups"

endpoint_limiter = LimiterRequests(tags=tag_name,
                                   default_key='L1')

# ------------------------------------------------------------------------------------------------
#             GET PODS VOLUME BACKUP
# ------------------------------------------------------------------------------------------------

limiter_backups = endpoint_limiter.get_limiter_cust('pod_volume_backups')
route = '/pod-volume-backups'


@router.get(
    path=route,
    tags=[tag_name],
    summary='Get pod volume backups',
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
async def get_pvbs():
    return await get_pod_volume_backups_handler()


# ------------------------------------------------------------------------------------------------
#             GET POD VOLUME BACKUP DETAILS
# ------------------------------------------------------------------------------------------------


limiter_backup = endpoint_limiter.get_limiter_cust('pod_volume_backup')
route = '/pod-volume-backup'


@router.get(
    path=route,
    tags=[tag_name],
    summary='Get pod volume',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter_backup.max_request,
                                  limiter_seconds=limiter_backup.seconds),
    dependencies=[Depends(RateLimiter(interval_seconds=limiter_backup.seconds,
                                      max_requests=limiter_backup.max_request))],
    response_model=SuccessfulRequest,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def get_pvb_details(backup_name: str):
    return await get_pod_volume_backup_details_handler(backup_name)

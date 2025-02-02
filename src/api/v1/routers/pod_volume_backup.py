from fastapi import APIRouter, status, Depends
from typing import Union

from core.config import ConfigHelper
from security.service.helpers.rate_limiter import RateLimiter, LimiterRequests

from utils.commons import route_description
from utils.handle_exceptions import handle_exceptions_endpoint

from api.common.response_model.failed_request import FailedRequest
from api.common.response_model.successful_request import SuccessfulRequest

from api.v1.controllers.pod_volume_backup import PodVolumeBackup

router = APIRouter()
pvb = PodVolumeBackup()

config_app = ConfigHelper()

tag_name = "Pod Volume Backups"

endpoint_limiter = LimiterRequests(tags=tag_name,
                                   default_key='L1')

limiter_backups = endpoint_limiter.get_limiter_cust('pod_volume_backups')
route = '/pod-volume-backups'


@router.get(path=route,
            tags=[tag_name],
            summary='Get pod volume backups',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter_backups.max_request,
                                          limiter_seconds=limiter_backups.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_backups.seconds,
                                              max_requests=limiter_backups.max_request))],
            response_model=Union[SuccessfulRequest, FailedRequest],
            status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def get_pvbs():
    return await pvb.get_pod_volume_backups()


limiter_backup = endpoint_limiter.get_limiter_cust('pod_volume_backup')
route = '/pod-volume-backup'


@router.get(path=route,
            tags=[tag_name],
            summary='Get pod volume',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter_backup.max_request,
                                          limiter_seconds=limiter_backup.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_backup.seconds,
                                              max_requests=limiter_backup.max_request))],
            response_model=Union[SuccessfulRequest, FailedRequest],
            status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def get_pvb(backup_name=None):
    return await pvb.get_pod_volume_backup(backup_name)

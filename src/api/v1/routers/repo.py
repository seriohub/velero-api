from fastapi import APIRouter, Depends, status
from typing import Union

from core.config import ConfigHelper
from security.rate_limiter import RateLimiter, LimiterRequests

from utils.commons import route_description
from utils.handle_exceptions import handle_exceptions_endpoint
from helpers.printer import PrintHelper

from api.common.response_model.failed_request import FailedRequest
from api.common.response_model.successful_request import SuccessfulRequest

from api.v1.controllers.repo import Repo

router = APIRouter()
repo = Repo()
config_app = ConfigHelper()

print_ls = PrintHelper('[v1.routers.repo]',
                       level=config_app.get_internal_log_level())

tag_name = 'Repository'

endpoint_limiter = LimiterRequests(printer=print_ls,
                                   tags=tag_name,
                                   default_key='L1')

limiter = endpoint_limiter.get_limiter_cust("repo_get")
route = '/repo/get'


@router.get(path=route,
            tags=[tag_name],
            summary='Get backups repository',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter.max_request,
                                          limiter_seconds=limiter.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter.seconds,
                                              max_requests=limiter.max_request))],
            response_model=Union[SuccessfulRequest, FailedRequest],
            status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def get():
    return await repo.get()


limiter = endpoint_limiter.get_limiter_cust("repo_lock_check")
route = '/repo/locks/get'


@router.get(path=route,
            tags=[tag_name],
            summary='Get repository locks',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter.max_request,
                                          limiter_seconds=limiter.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter.seconds,
                                              max_requests=limiter.max_request))],
            response_model=Union[SuccessfulRequest, FailedRequest],
            status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def get(repository_url: str = None):
    return await repo.get_locks(repository_url)

limiter = endpoint_limiter.get_limiter_cust("repo_unlock")
route = '/repo/unlock'


@router.get(path=route,
            tags=[tag_name],
            summary='Unlock restic repository',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter.max_request,
                                          limiter_seconds=limiter.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter.seconds,
                                              max_requests=limiter.max_request))],
            response_model=Union[SuccessfulRequest, FailedRequest],
            status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def get(repository_url: str = None, remove_all: bool = False):
    return await repo.unlock(repository_url, remove_all)


limiter = endpoint_limiter.get_limiter_cust("repo_check")
route = '/repo/check'


@router.get(path=route,
            tags=[tag_name],
            summary='Check restic repository',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter.max_request,
                                          limiter_seconds=limiter.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter.seconds,
                                              max_requests=limiter.max_request))],
            response_model=Union[SuccessfulRequest, FailedRequest],
            status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def check(repository_url: str = None):
    return await repo.check(repository_url)

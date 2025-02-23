from fastapi import APIRouter, Depends, status

from configs.response import common_error_authenticated_response

from security.helpers.rate_limiter import RateLimiter, LimiterRequests

from utils.commons import route_description
from utils.handle_exceptions import handle_exceptions_endpoint

from schemas.response.successful_request import SuccessfulRequest
from schemas.request.unlock_restic_repo import UnlockResticRepoRequestSchema

from controllers.repo import (get_repos_handler,
                              get_backup_size_handler,
                              get_repo_locks_handler,
                              unlock_repo_handler,
                              check_repo_handler)

from configs.config_boot import config_app

router = APIRouter()

tag_name = 'Repository'

endpoint_limiter = LimiterRequests(tags=tag_name,
                                   default_key='L1')

# ------------------------------------------------------------------------------------------------
#             GET REPOS
# ------------------------------------------------------------------------------------------------


limiter_repos = endpoint_limiter.get_limiter_cust("repos")
route = '/repos'


@router.get(
    path=route,
    tags=[tag_name],
    summary='Get backups repository',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter_repos.max_request,
                                  limiter_seconds=limiter_repos.seconds),
    dependencies=[Depends(RateLimiter(interval_seconds=limiter_repos.seconds,
                                      max_requests=limiter_repos.max_request))],
    response_model=SuccessfulRequest,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def get_repos():
    return await get_repos_handler()


# ------------------------------------------------------------------------------------------------
#             GET REPOS SIZE
# ------------------------------------------------------------------------------------------------


limiter_size = endpoint_limiter.get_limiter_cust("repo_size")
route = '/repo/size'


@router.get(
    path=route,
    tags=[tag_name],
    summary='Get size (Mb) of a repository',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter_size.max_request,
                                  limiter_seconds=limiter_size.seconds),
    dependencies=[Depends(RateLimiter(interval_seconds=limiter_size.seconds,
                                      max_requests=limiter_size.max_request))],
    response_model=SuccessfulRequest,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def get_repo_size(repository_url: str = None,
                        backup_storage_location: str = None,
                        repository_name: str = None,
                        repository_type: str = None,
                        volume_namespace: str = None,
                        ):
    return await get_backup_size_handler(repository_url=repository_url,
                                         backup_storage_location=backup_storage_location,
                                         repository_name=repository_name,
                                         repository_type=repository_type,
                                         volume_namespace=volume_namespace
                                         )


# ------------------------------------------------------------------------------------------------
#             CHECK RESTIC REPO LOCK
# ------------------------------------------------------------------------------------------------


limiter_locks = endpoint_limiter.get_limiter_cust("repo_lock_check")
route = '/repo/locks'


@router.get(
    path=route,
    tags=[tag_name],
    summary='Get repository locks',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter_locks.max_request,
                                  limiter_seconds=limiter_locks.seconds),
    dependencies=[Depends(RateLimiter(interval_seconds=limiter_locks.seconds,
                                      max_requests=limiter_locks.max_request))],
    response_model=SuccessfulRequest,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def get_repos_locks(bsl: str, repository_url: str = None):
    return await get_repo_locks_handler(bsl, repository_url)


# ------------------------------------------------------------------------------------------------
#             UNLOCK RESTIC REPO
# ------------------------------------------------------------------------------------------------


limiter_unlock = endpoint_limiter.get_limiter_cust("repo_unlock")
route = '/repo/unlock'


@router.post(path=route,
             tags=[tag_name],
             summary='Unlock restic repository',
             description=route_description(tag=tag_name,
                                           route=route,
                                           limiter_calls=limiter_unlock.max_request,
                                           limiter_seconds=limiter_unlock.seconds),
             dependencies=[Depends(RateLimiter(interval_seconds=limiter_unlock.seconds,
                                               max_requests=limiter_unlock.max_request))],
             response_model=SuccessfulRequest,
             responses=common_error_authenticated_response,
             status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def unlock_repo(repo: UnlockResticRepoRequestSchema):
    return await unlock_repo_handler(repo=repo)


# ------------------------------------------------------------------------------------------------
#             CHECK RESTIC REPO
# ------------------------------------------------------------------------------------------------


limiter_check = endpoint_limiter.get_limiter_cust("repo_check")
route = '/repo/check'


@router.get(
    path=route,
    tags=[tag_name],
    summary='Check restic repository',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter_check.max_request,
                                  limiter_seconds=limiter_check.seconds),
    dependencies=[Depends(RateLimiter(interval_seconds=limiter_check.seconds,
                                      max_requests=limiter_check.max_request))],
    response_model=SuccessfulRequest,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_200_OK)
@handle_exceptions_endpoint
async def check_repo(bsl: str, repository_url: str = None):
    return await check_repo_handler(bsl, repository_url)

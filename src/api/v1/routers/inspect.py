from fastapi import APIRouter, Depends, status

from constants.response import common_error_authenticated_response
from vui_common.schemas.response.successful_request import SuccessfulRequest

from vui_common.security.helpers.rate_limiter import RateLimiter, LimiterRequests

from vui_common.utils.swagger import route_description
from vui_common.utils.exceptions import handle_exceptions_endpoint

from controllers.inspect import (get_backups_handler,
                                 # get_folders_handler,
                                 get_file_content_handler,
                                 get_recursive_directory_contents_handler)

router = APIRouter()

tag_name = "Inspect"
endpoint_limiter = LimiterRequests(tags=tag_name,
                                   default_key='L1')

# ------------------------------------------------------------------------------------------------
#             GET AVAILABLE BACKUP FOR INSPECT
# ------------------------------------------------------------------------------------------------


limiter_backups = endpoint_limiter.get_limiter_cust('inspect_backups')
route = '/inspect/backups'


@router.get(
    path=route,
    tags=[tag_name],
    summary='Get list folder available',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter_backups.max_request,
                                  limiter_seconds=limiter_backups.seconds),
    dependencies=[Depends(RateLimiter(interval_seconds=limiter_backups.seconds,
                                      max_requests=limiter_backups.max_request))],
    response_model=SuccessfulRequest,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_200_OK
)
@handle_exceptions_endpoint
async def get_backups():
    return await get_backups_handler()


# ------------------------------------------------------------------------------------------------
#             GET FOLDERS
# ------------------------------------------------------------------------------------------------

# limiter_backups = endpoint_limiter.get_limiter_cust('inspect_folders')
# route = '/inspect/folders'
#
#
# @router.get(
#     path=route,
#     tags=[tag_name],
#     summary='Get list folders',
#     description=route_description(tag=tag_name,
#                                   route=route,
#                                   limiter_calls=limiter_backups.max_request,
#                                   limiter_seconds=limiter_backups.seconds),
#     dependencies=[Depends(RateLimiter(interval_seconds=limiter_backups.seconds,
#                                       max_requests=limiter_backups.max_request))],
#     response_model=SuccessfulRequest,
#     responses=common_error_authenticated_response,
#     status_code=status.HTTP_200_OK
# )
# @handle_exceptions_endpoint
# async def get_folders(path: str):
#     return await get_folders_handler(path=path)


# ------------------------------------------------------------------------------------------------
#             GET FILE CONTENT
# ------------------------------------------------------------------------------------------------

limiter_backups = endpoint_limiter.get_limiter_cust('inspect_folders')
route = '/inspect/file'


@router.get(
    path=route,
    tags=[tag_name],
    summary='Get list folders',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter_backups.max_request,
                                  limiter_seconds=limiter_backups.seconds),
    dependencies=[Depends(RateLimiter(interval_seconds=limiter_backups.seconds,
                                      max_requests=limiter_backups.max_request))],
    response_model=SuccessfulRequest,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_200_OK
)
@handle_exceptions_endpoint
async def get_file_content(path: str):
    return await get_file_content_handler(path=path)

# ------------------------------------------------------------------------------------------------
#             GET RECURSIVE FOLDER CONTENT
# ------------------------------------------------------------------------------------------------

limiter_backups = endpoint_limiter.get_limiter_cust('inspect_folder_content')
route = '/inspect/folder/content'


@router.get(
    path=route,
    tags=[tag_name],
    summary='Get folder content',
    description=route_description(tag=tag_name,
                                  route=route,
                                  limiter_calls=limiter_backups.max_request,
                                  limiter_seconds=limiter_backups.seconds),
    dependencies=[Depends(RateLimiter(interval_seconds=limiter_backups.seconds,
                                      max_requests=limiter_backups.max_request))],
    response_model=SuccessfulRequest,
    responses=common_error_authenticated_response,
    status_code=status.HTTP_200_OK
)
@handle_exceptions_endpoint
async def get_folder_content(backup: str):
    return await get_recursive_directory_contents_handler(backup=backup)



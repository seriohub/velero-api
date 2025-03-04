import os
from fastapi.responses import JSONResponse

from schemas.response.successful_request import SuccessfulRequest
from schemas.notification import Notification
from schemas.message import Message
from schemas.request.unlock_restic_repo import UnlockResticRepoRequestSchema

from service.bsl import get_bsl_credentials_service
from service.repo import (get_repos_service,
                          get_repo_backup_size_service,
                          get_restic_repo_locks_service,
                          unlock_restic_repo_service,
                          check_restic_repo_service)


async def get_repos_handler():
    payload = await get_repos_service()

    response = SuccessfulRequest(payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=200)


async def get_backup_size_handler(repository_url: str = None,
                                  backup_storage_location: str = None,
                                  repository_name: str = None,
                                  repository_type: str = None,
                                  volume_namespace: str = None
                                  ):
    payload = await get_repo_backup_size_service(repository_url=repository_url,
                                                 backup_storage_location=backup_storage_location,
                                                 repository_name=repository_name,
                                                 repository_type=repository_type,
                                                 volume_namespace=volume_namespace)

    response = SuccessfulRequest(payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=200)


async def get_restic_repo_locks_handler(bsl, repository_url):
    aws_access_key_id, aws_secret_access_key = await get_bsl_credentials_service(backup_storage_location=bsl)
    env = {
        **os.environ,
        "AWS_ACCESS_KEY_ID": aws_access_key_id,
        "AWS_SECRET_ACCESS_KEY": aws_secret_access_key
    }
    payload = await get_restic_repo_locks_service(env, repository_url)

    msg = Notification(title='Get locks',
                       description=f"{len(payload[repository_url])} locks found",
                       type_='INFO')

    response = SuccessfulRequest(payload=payload, notifications=[msg])
    return JSONResponse(content=response.model_dump(), status_code=200)


async def unlock_restic_repo_handler(repo: UnlockResticRepoRequestSchema):
    aws_access_key_id, aws_secret_access_key = await get_bsl_credentials_service(backup_storage_location=repo.bsl)
    env = {
        **os.environ,
        "AWS_ACCESS_KEY_ID": aws_access_key_id,
        "AWS_SECRET_ACCESS_KEY": aws_secret_access_key
    }
    payload = await unlock_restic_repo_service(env, repo.bsl, repo.repositoryUrl, repo.removeAll)

    response = SuccessfulRequest(payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=200)


async def check_restic_repo_handler(bsl, repository_url):
    aws_access_key_id, aws_secret_access_key = await get_bsl_credentials_service(backup_storage_location=bsl)
    env = {
        **os.environ,
        "AWS_ACCESS_KEY_ID": aws_access_key_id,
        "AWS_SECRET_ACCESS_KEY": aws_secret_access_key
    }
    payload = await check_restic_repo_service(env, repository_url)

    msg = Message(title=f"Check {repository_url}",
                  description=payload[repository_url],
                  type_='INFO')

    response = SuccessfulRequest(messages=[msg])
    return JSONResponse(content=response.model_dump(), status_code=200)

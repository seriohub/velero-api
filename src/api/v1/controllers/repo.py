import os
from fastapi.responses import JSONResponse

from utils.handle_exceptions import handle_exceptions_controller

from api.common.response_model.successful_request import SuccessfulRequest
from api.common.response_model.failed_request import FailedRequest
from api.common.response_model.message import Message

from api.v1.schemas.unlock_restic_repo import UnlockResticRepo

from service.repo_service import RepoService
from service.backup_location_service import BackupLocationService
from service.k8s_service import K8sService

repoService = RepoService()
bSL = BackupLocationService()
k8s = K8sService()

class Repo:

    @handle_exceptions_controller
    async def get(self):
        payload = await repoService.get()

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        response = SuccessfulRequest(payload=payload['data'])
        return JSONResponse(content=response.toJSON(), status_code=200)

    @handle_exceptions_controller
    async def get_backup_size(self,
                              repository_url: str = None,
                              endpoint: str = None,
                              backup_storage_location: str = None,
                              repository_name: str = None,
                              repository_type: str = None,
                              volume_namespace: str = None
                              ):
        payload = await repoService.get_backup_size(repository_url=repository_url,
                                                    backup_storage_location=backup_storage_location,
                                                    repository_name=repository_name,
                                                    repository_type=repository_type,
                                                    volume_namespace=volume_namespace)

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        response = SuccessfulRequest(payload=payload['data'])
        return JSONResponse(content=response.toJSON(), status_code=200)

    @handle_exceptions_controller
    async def get_locks(self, bsl, repository_url):
        # output = await bSL.get(backup_storage_location=bsl)
        # bs = output['data'][0]
        # print(bs)
        # if 'credentials' in bs['spec']:
        #     secret_name = bs['spec']['credentials']['name']
        #     secret_key = bs['spec']['credentials']['key']
        #     credentials = await k8s.get_credential(secret_name, secret_key)
        # else:
        #     credentials = await k8s.get_default_credential()
        #
        # credentials = credentials['data']
        aws_access_key_id, aws_secret_access_key = await bSL.credentials(backup_storage_location=bsl)
        env = {
            **os.environ,
            "AWS_ACCESS_KEY_ID": aws_access_key_id,
            "AWS_SECRET_ACCESS_KEY": aws_secret_access_key
        }
        payload = await repoService.get_locks(env, repository_url)

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        msg = Message(title='Get locks',
                      description=f"{len(payload['data'][repository_url])} locks found",
                      type='INFO')

        response = SuccessfulRequest(payload=payload['data'], notifications=[msg.toJSON()])
        return JSONResponse(content=response.toJSON(), status_code=200)

    @handle_exceptions_controller
    async def unlock(self, unlock_repo: UnlockResticRepo):

        aws_access_key_id, aws_secret_access_key = await bSL.credentials(backup_storage_location=unlock_repo.bsl)
        env = {
            **os.environ,
            "AWS_ACCESS_KEY_ID": aws_access_key_id,
            "AWS_SECRET_ACCESS_KEY": aws_secret_access_key
        }
        payload = await repoService.unlock(env, unlock_repo.bsl, unlock_repo.repositoryUrl, unlock_repo.removeAll)

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        response = SuccessfulRequest(payload=payload['data'])
        return JSONResponse(content=response.toJSON(), status_code=200)

    @handle_exceptions_controller
    async def check(self, bsl, repository_url):

        aws_access_key_id, aws_secret_access_key = await bSL.credentials(backup_storage_location=bsl)
        env = {
            **os.environ,
            "AWS_ACCESS_KEY_ID": aws_access_key_id,
            "AWS_SECRET_ACCESS_KEY": aws_secret_access_key
        }
        payload = await repoService.check(env, repository_url)

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        msg = Message(title=f"Check {repository_url}",
                      description=payload['data'][repository_url],
                      type='INFO')

        response = SuccessfulRequest(messages=[msg.toJSON()])
        return JSONResponse(content=response.toJSON(), status_code=200)

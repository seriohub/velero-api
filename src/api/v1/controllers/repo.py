from fastapi.responses import JSONResponse

from utils.handle_exceptions import handle_exceptions_controller

from api.common.response_model.successful_request import SuccessfulRequest
from api.common.response_model.failed_request import FailedRequest
from api.common.response_model.message import Message

from service.repo_service import RepoService


repoService = RepoService()


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
    async def get_locks(self, repository_url):
        payload = await repoService.get_locks(repository_url)

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        msg = Message(title='Get locks',
                      description=f"{len(payload['data'][repository_url])} locks found",
                      type='INFO')

        response = SuccessfulRequest(payload=payload['data'], messages=[msg.toJSON()])
        return JSONResponse(content=response.toJSON(), status_code=200)

    @handle_exceptions_controller
    async def unlock(self, repository_url, remove_all):
        payload = await repoService.unlock(repository_url, remove_all)

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        response = SuccessfulRequest(payload=payload['data'])
        return JSONResponse(content=response.toJSON(), status_code=200)

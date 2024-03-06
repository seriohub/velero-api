from fastapi.responses import JSONResponse

from utils.handle_exceptions import handle_exceptions_controller

from api.common.response_model.failed_request import FailedRequest
from api.common.response_model.successful_request import SuccessfulRequest

from service.k8s_service import K8sService


k8sService = K8sService()

class K8s:

    @handle_exceptions_controller
    async def get_ns(self):
        payload = await k8sService.get_ns()

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        response = SuccessfulRequest(payload=payload['data'])
        return JSONResponse(content=response.toJSON(), status_code=200)

    @handle_exceptions_controller
    async def get_resources(self):
        payload = await k8sService.get_ns()

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        response = SuccessfulRequest(payload=payload['data'])
        return JSONResponse(content=response.toJSON(), status_code=200)

    @handle_exceptions_controller
    async def get_credential(self, secret_name, secret_key):
        if not secret_name or not secret_key:
            failed_response = FailedRequest(title="Error",
                                            description="Secret name and secret key are required")
            return JSONResponse(content=failed_response.toJSON(), status_code=400)

        payload = await k8sService.get_credential(secret_name, secret_key)

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        response = SuccessfulRequest(payload=payload['data'])
        return JSONResponse(content=response.toJSON(), status_code=200)

    @handle_exceptions_controller
    async def get_default_credential(self):
        payload = await k8sService.get_default_credential()

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        response = SuccessfulRequest(payload=payload['data'])
        return JSONResponse(content=response.toJSON(), status_code=200)

    @handle_exceptions_controller
    async def get_k8s_storage_classes(self):
        payload = await k8sService.get_storage_classes()

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        response = SuccessfulRequest(payload=payload['data'])
        return JSONResponse(content=response.toJSON(), status_code=200)

    @handle_exceptions_controller
    async def get_logs(self, lines=100, follow=False):

        payload = await k8sService.get_logs(lines=lines, follow=follow)

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        response = SuccessfulRequest(payload=payload['data'])
        return JSONResponse(content=response.toJSON(), status_code=200)



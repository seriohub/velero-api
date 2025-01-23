from fastapi.responses import JSONResponse

from utils.handle_exceptions import handle_exceptions_controller
from api.common.response_model.successful_request import SuccessfulRequest
from api.common.response_model.failed_request import FailedRequest

from service.k8s_service import K8sService


k8s = K8sService()

class Health:

    @handle_exceptions_controller
    async def get_k8s_online(self):
        payload = (await k8s.get_k8s_online())

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        response = SuccessfulRequest(payload=payload['data'])
        return JSONResponse(content=response.toJSON(), status_code=200)

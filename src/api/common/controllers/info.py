from fastapi.responses import JSONResponse

from utils.handle_exceptions import handle_exceptions_controller
from core.config import ConfigHelper

from api.common.response_model.successful_request import SuccessfulRequest
from api.common.response_model.failed_request import FailedRequest

from service.info_service import InfoService

configApp = ConfigHelper()
infoService = InfoService()

class Info:

    @handle_exceptions_controller
    async def identify_architecture(self):
        payload = await infoService.identify_architecture()

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        response = SuccessfulRequest(payload=payload['data'])
        return JSONResponse(content=response.toJSON(), status_code=200)

    @handle_exceptions_controller
    async def get_origins(self):
        payload = configApp.get_origins()

        response = SuccessfulRequest(payload=payload)
        return JSONResponse(content=response.toJSON(), status_code=200)

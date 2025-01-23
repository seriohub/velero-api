from fastapi.responses import JSONResponse

from utils.handle_exceptions import handle_exceptions_controller
from core.config import ConfigHelper

from api.common.response_model.successful_request import SuccessfulRequest
from api.common.response_model.failed_request import FailedRequest

from service.watchdog_service import WatchdogService
from service.info_service import InfoService

configApp = ConfigHelper()
infoService = InfoService()
watchdog = WatchdogService()


class Agent:

    @handle_exceptions_controller
    async def watchdog_online(self):
        payload = await watchdog.online()

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        response = SuccessfulRequest(payload=payload['data'])
        return JSONResponse(content=response.toJSON(), status_code=200)

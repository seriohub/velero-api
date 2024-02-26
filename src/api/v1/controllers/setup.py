import os
from fastapi.responses import JSONResponse

from utils.handle_exceptions import handle_exceptions_controller
from core.config import ConfigHelper


from api.common.response_model.successful_request import SuccessfulRequest
from api.common.response_model.failed_request import FailedRequest

from service.k8s_service import K8sService
from service.setup_service import SetupService

from api.v1.controllers.schedule import Schedule


schedule = Schedule()
k8sService = K8sService()
config_app = ConfigHelper()
setupService = SetupService()

class Setup:

    @handle_exceptions_controller
    async def get_env(self):
        if os.getenv('K8S_IN_CLUSTER_MODE').lower() == 'true':
            output = await k8sService.get_config_map(namespace=config_app.get_k8s_velero_ui_namespace())
            env_data = output['data']
        else:
            env_data = config_app.get_env_variables()

        response = SuccessfulRequest(payload=env_data)
        return JSONResponse(content=response.toJSON(), status_code=200)

    @handle_exceptions_controller
    async def version(self):
        payload = await setupService.version()

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        response = SuccessfulRequest(payload=payload['data'])
        return JSONResponse(content=response.toJSON(), status_code=200)

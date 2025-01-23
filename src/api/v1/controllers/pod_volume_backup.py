from fastapi.responses import JSONResponse

from utils.handle_exceptions import handle_exceptions_controller
from api.common.response_model.failed_request import FailedRequest
from api.common.response_model.successful_request import SuccessfulRequest


from service.k8s_service import K8sService


k8s = K8sService()


class PodVolumeBackup:

    def __init__(self):
        pass

    @handle_exceptions_controller
    async def get_pod_volume_backups(self):
        payload = await k8s.get_pod_volume_backups()

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        response = SuccessfulRequest(payload=payload['data'])
        return JSONResponse(content=response.toJSON(), status_code=200)

    @handle_exceptions_controller
    async def get_pod_volume_backup(self, backup_name):
        payload = await k8s.get_pod_volume_backup(backup_name)

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        response = SuccessfulRequest(payload=payload['data'])
        return JSONResponse(content=response.toJSON(), status_code=200)


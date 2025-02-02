from fastapi.responses import JSONResponse

from utils.handle_exceptions import handle_exceptions_controller

from api.common.response_model.failed_request import FailedRequest
from api.common.response_model.successful_request import SuccessfulRequest

from api.v1.schemas.create_cloud_credentials import CreateCloudCredentials

from service.k8s_service import K8sService
from core.config import ConfigHelper

k8s = K8sService()
configApp = ConfigHelper()

class K8s:

    @handle_exceptions_controller
    async def get_ns(self):
        payload = await k8s.get_namespaces()

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        response = SuccessfulRequest(payload=payload['data'])
        return JSONResponse(content=response.toJSON(), status_code=200)

    @handle_exceptions_controller
    async def get_resources(self):
        payload = await k8s.get_namespaces()

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        response = SuccessfulRequest(payload=payload['data'])
        return JSONResponse(content=response.toJSON(), status_code=200)

    @handle_exceptions_controller
    async def get_credential(self, secret_name, secret_key):
        if not secret_name or not secret_key:
            failed_response = FailedRequest(title="Error", description="Secret name and secret key are required")
            return JSONResponse(content=failed_response.toJSON(), status_code=400)

        payload = await k8s.get_credential(secret_name, secret_key)

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        response = SuccessfulRequest(payload=payload['data'])
        return JSONResponse(content=response.toJSON(), status_code=200)

    @handle_exceptions_controller
    async def get_default_credential(self):
        payload = await k8s.get_default_credential()

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        response = SuccessfulRequest(payload=payload['data'])
        return JSONResponse(content=response.toJSON(), status_code=200)

    @handle_exceptions_controller
    async def get_k8s_storage_classes(self):
        payload = await k8s.get_storage_classes()

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        response = SuccessfulRequest(payload=payload['data'])
        return JSONResponse(content=response.toJSON(), status_code=200)

    @handle_exceptions_controller
    async def get_logs(self, lines=100, follow=False):

        payload = await k8s.get_logs(lines=lines, follow=follow)

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        response = SuccessfulRequest(payload=payload['data'])
        return JSONResponse(content=response.toJSON(), status_code=200)

    @handle_exceptions_controller
    async def create_cloud_credentials(self, cloud_credentials: CreateCloudCredentials):
        # if (
        #         not cloud_credentials.newSecretName or not cloud_credentials.awsAccessKeyId or not
        # cloud_credentials.awsSecretAccessKey):
        if any(not value for value in [cloud_credentials.newSecretName, cloud_credentials.awsAccessKeyId,
                                       cloud_credentials.awsSecretAccessKey]):
            failed_response = FailedRequest(title="Error",
                                            description="Secret name, aws access key id and aws secret access key are "
                                                        "required")
            return JSONResponse(content=failed_response.toJSON(), status_code=400)

        payload = await k8s.create_cloud_credentials_secret(cloud_credentials.newSecretName,
                                                            cloud_credentials.newSecretKey,
                                                            cloud_credentials.awsAccessKeyId,
                                                            cloud_credentials.awsSecretAccessKey)

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        response = SuccessfulRequest()
        return JSONResponse(content=response.toJSON(), status_code=200)

    @handle_exceptions_controller
    async def get_velero_secret(self):

        payload = await k8s.get_velero_secret()

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        response = SuccessfulRequest(payload=payload['data'])
        return JSONResponse(content=response.toJSON(), status_code=200)

    @handle_exceptions_controller
    async def get_velero_secret_key(self, secret_name):

        payload = await k8s.get_secret_keys(configApp.get_k8s_velero_namespace(), secret_name)

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        response = SuccessfulRequest(payload=payload['data'])
        return JSONResponse(content=response.toJSON(), status_code=200)

    async def get_manifest(self, resource_type, resource_name):
        payload = await k8s.get_resource_manifest(resource_type=resource_type, resource_name=resource_name)

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        response = SuccessfulRequest(payload=payload['data'])
        return JSONResponse(content=response.toJSON(), status_code=200)


from fastapi.responses import JSONResponse

from utils.handle_exceptions import handle_exceptions_controller
from utils.commons import is_valid_name

from api.common.response_model.failed_request import FailedRequest
from api.common.response_model.successful_request import SuccessfulRequest
from api.common.response_model.message import Message

from service.restore_service import RestoreService

serviceRestore = RestoreService()

class Restore:

    @handle_exceptions_controller
    async def get(self, in_progress=False, publish_message=True):
        payload = await serviceRestore.get(in_progress=in_progress, publish_message=publish_message)

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        response = SuccessfulRequest(payload=payload['data'])
        return JSONResponse(content=response.toJSON(), status_code=200)

    @handle_exceptions_controller
    async def create(self, req_info):
        resource_type = req_info['resource_type']
        backup_name = req_info['resource_name']

        if backup_name == '':
            failed_response = FailedRequest(title="Error",
                                            description="Invalid request. You can only provide a backup name.")
            return JSONResponse(content=failed_response.toJSON(), status_code=400)

        if not is_valid_name(backup_name):
            failed_response = FailedRequest(title="Error",
                                            description="Invalid resource name.")
            return JSONResponse(content=failed_response.toJSON(), status_code=400)

        payload = await serviceRestore.create(req_info=req_info)

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        msg = Message(title='Create Restore',
                      description=f"Restore from {resource_type} {backup_name} created successfully",
                      type='INFO')
        response = SuccessfulRequest(messages=[msg.toJSON()])
        return JSONResponse(content=response.toJSON(), status_code=201)

    @handle_exceptions_controller
    async def logs(self, restore_name):
        if not restore_name:
            failed_response = FailedRequest(title="Error",
                                            description="Restore name is required.")
            return JSONResponse(content=failed_response.toJSON(), status_code=400)

        payload = await serviceRestore.logs(restore_name=restore_name)

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        response = SuccessfulRequest(payload=payload['data'])
        return JSONResponse(content=response.toJSON(), status_code=200)

    @handle_exceptions_controller
    async def describe(self, restore_name):
        if not restore_name:
            failed_response = FailedRequest(title="Error",
                                            description="Restore name is required.")
            return JSONResponse(content=failed_response.toJSON(), status_code=400)

        payload = await serviceRestore.describe(restore_name=restore_name)

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        response = SuccessfulRequest(payload=payload['data'])
        return JSONResponse(content=response.toJSON(), status_code=200)

    @handle_exceptions_controller
    async def delete(self, restore_name):
        if not restore_name:
            failed_response = FailedRequest(title="Error",
                                            description="Restore name is required.")
            return JSONResponse(content=failed_response.toJSON(), status_code=400)

        payload = await serviceRestore.delete(restore_name=restore_name)

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        msg = Message(title='Delete restore',
                      description=f"Restore {restore_name} deleted request done!",
                      type='INFO')
        response = SuccessfulRequest(messages=[msg.toJSON()])
        return JSONResponse(content=response.toJSON(), status_code=200)

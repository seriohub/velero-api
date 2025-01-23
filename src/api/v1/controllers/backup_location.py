from fastapi.responses import JSONResponse

from utils.handle_exceptions import handle_exceptions_controller

from api.common.response_model.successful_request import SuccessfulRequest
from api.common.response_model.failed_request import FailedRequest

from service.backup_location_service import BackupLocationService
from api.common.response_model.message import Message

from api.v1.schemas.create_bsl import CreateBsl
from api.v1.schemas.default_bsl import DefaultBsl
from api.v1.schemas.delete_bsl import DeleteBsl

backupLocationService = BackupLocationService()


class BackupLocation:

    @handle_exceptions_controller
    async def get(self):
        payload = await backupLocationService.get()

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        response = SuccessfulRequest(payload=payload['data'])
        return JSONResponse(content=response.toJSON(), status_code=200)

    @handle_exceptions_controller
    async def create(self, create_bsl: CreateBsl):
        payload = await backupLocationService.create(create_bsl)

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        msg = Message(title='Create bsl', description=f"BSL {create_bsl.name} created!", type='INFO')
        response = SuccessfulRequest(notifications=[msg.toJSON()])
        return JSONResponse(content=response.toJSON(), status_code=201)

    @handle_exceptions_controller
    async def default(self, default_bsl: DefaultBsl):
        await backupLocationService.remove_current_default()
        payload = await backupLocationService.default(default_bsl.name, True)

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        msg = Message(title='Default bsl', description=f"BSL {default_bsl.name} set as default!", type='INFO')
        response = SuccessfulRequest(notifications=[msg.toJSON()])
        return JSONResponse(content=response.toJSON(), status_code=201)

    @handle_exceptions_controller
    async def remove_default(self, default_bsl: DefaultBsl):
        payload = await backupLocationService.default(default_bsl.name, False)

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        msg = Message(title='Default bsl', description=f"BSL {default_bsl.name} removed as default!", type='INFO')
        response = SuccessfulRequest(notifications=[msg.toJSON()])
        return JSONResponse(content=response.toJSON(), status_code=201)

    @handle_exceptions_controller
    async def delete(self, bsl_delete: DeleteBsl):
        if not bsl_delete.resourceName:
            failed_response = FailedRequest(title="Error", description="Bsl name is required")
            return JSONResponse(content=failed_response.toJSON(), status_code=400)

        payload = await backupLocationService.delete(bsl_name=bsl_delete.resourceName)

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        msg = Message(title='Delete bsl', description=f'Bsl {bsl_delete.resourceName} deleted request done!', type='INFO')

        response = SuccessfulRequest()
        response.notifications = [msg.toJSON()]
        return JSONResponse(content=response.toJSON(), status_code=200)

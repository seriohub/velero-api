from fastapi.responses import JSONResponse

from utils.handle_exceptions import handle_exceptions_controller

from api.common.response_model.successful_request import SuccessfulRequest
from api.common.response_model.failed_request import FailedRequest

from service.snapshot_location_service import SnapshotLocationService

from api.common.response_model.message import Message

from api.v1.schemas.create_vsl import CreateVsl
from api.v1.schemas.delete_vsl import DeleteVsl


snapshotLocationService = SnapshotLocationService()


class SnapshotLocation:

    @handle_exceptions_controller
    async def get(self):
        payload = await snapshotLocationService.get()

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        response = SuccessfulRequest(payload=payload['data'])
        return JSONResponse(content=response.toJSON(), status_code=200)

    @handle_exceptions_controller
    async def create(self, create_bsl: CreateVsl):
        payload = await snapshotLocationService.create(create_bsl)

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        msg = Message(title='Create bsl', description=f"BSL {create_bsl.name} created!", type='INFO')
        response = SuccessfulRequest(notifications=[msg.toJSON()])
        return JSONResponse(content=response.toJSON(), status_code=201)

    @handle_exceptions_controller
    async def delete(self, bsl_delete: DeleteVsl):
        if not bsl_delete.resourceName:
            failed_response = FailedRequest(title="Error", description="Bsl name is required")
            return JSONResponse(content=failed_response.toJSON(), status_code=400)

        payload = await snapshotLocationService.delete(vsl_name=bsl_delete.resourceName)

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        msg = Message(title='Delete bsl', description=f'Bsl {bsl_delete.resourceName} deleted request done!', type='INFO')

        response = SuccessfulRequest()
        response.notifications = [msg.toJSON()]
        return JSONResponse(content=response.toJSON(), status_code=200)
from fastapi.responses import JSONResponse

from api.common.response_model.failed_request import FailedRequest
from api.common.response_model.successful_request import SuccessfulRequest
from api.common.response_model.message import Message

from utils.handle_exceptions import handle_exceptions_controller


from service.sc_mapping_service import ScMappingService


scMappingService = ScMappingService()


class SCMapping:

    @handle_exceptions_controller
    async def get_storages_classes_map(self):
        payload = await scMappingService.get_storages_classes_map()

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        response = SuccessfulRequest(payload=payload['data'])
        return JSONResponse(content=response.toJSON(), status_code=200)

    @handle_exceptions_controller
    async def update_storages_classes_mapping(self,
                                              data_list=None):

        payload = await scMappingService.update_storages_classes_mapping(data_list=data_list)

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        msg = Message(title='Storage Class Map',
                      description=f"Done!",
                      type='INFO')
        response = SuccessfulRequest(notifications=[msg.toJSON()])
        return JSONResponse(content=response.toJSON(), status_code=200)

    @handle_exceptions_controller
    async def delete_storages_classes_mapping(self,
                                              data_list=None):
        payload = await scMappingService.delete_storages_classes_mapping(data_list=data_list)

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        msg = Message(title='Storage Class Map',
                      description=f"Deleted!",
                      type='INFO')
        response = SuccessfulRequest(notifications=[msg.toJSON()])
        return JSONResponse(content=response.toJSON(), status_code=200)

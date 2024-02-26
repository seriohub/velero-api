from fastapi.responses import JSONResponse

from utils.handle_exceptions import handle_exceptions_controller

from api.common.response_model.failed_request import FailedRequest
from api.common.response_model.successful_request import SuccessfulRequest
from api.common.response_model.message import Message

from service.schedule_service import ScheduleService
from service.k8s_service import K8sService

scheduleService = ScheduleService()
k8s = K8sService()

class Schedule:

    @handle_exceptions_controller
    async def get(self):
        payload = await scheduleService.get()

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        response = SuccessfulRequest(payload=payload['data'])
        return JSONResponse(content=response.toJSON(), status_code=200)

    @handle_exceptions_controller
    async def describe(self, schedule_name):
        if not schedule_name:
            failed_response = FailedRequest(title="Error",
                                            description="Schedule name is required")
            return JSONResponse(content=failed_response.toJSON(), status_code=400)

        payload = await scheduleService.describe(schedule_name=schedule_name)

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        response = SuccessfulRequest(payload=payload['data'])
        return JSONResponse(content=response.toJSON(), status_code=200)

    @handle_exceptions_controller
    async def pause(self, schedule_name):
        if not schedule_name:
            failed_response = FailedRequest(title="Error",
                                            description="Schedule name is required")
            return JSONResponse(content=failed_response.toJSON(), status_code=400)

        payload = await scheduleService.pause(schedule_name=schedule_name)

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        msg = Message(title='Pause schedule',
                      description=f"Schedule {schedule_name} pause request done!",
                      type='INFO')
        response = SuccessfulRequest(messages=[msg.toJSON()])
        return JSONResponse(content=response.toJSON(), status_code=200)

    @handle_exceptions_controller
    async def unpause(self, schedule_name):
        if not schedule_name:
            failed_response = FailedRequest(title="Error",
                                            description="Schedule name is required")
            return JSONResponse(content=failed_response.toJSON(), status_code=400)

        payload = await scheduleService.unpause(schedule_name=schedule_name)

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        msg = Message(title='Pause schedule',
                      description=f"Schedule {schedule_name} start request done!",
                      type='INFO')
        response = SuccessfulRequest(messages=[msg.toJSON()])
        return JSONResponse(content=response.toJSON(), status_code=200)

    @handle_exceptions_controller
    async def create(self, info):
        if not info.name or info.name == '':
            failed_response = FailedRequest(title="Error",
                                            description="Schedule name is required")
            return JSONResponse(content=failed_response.toJSON(), status_code=400)

        payload = await scheduleService.create(info=info)

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        msg = Message(title='Create schedule',
                      description=f"Schedule {info.name} created!",
                      type='INFO')
        response = SuccessfulRequest(messages=[msg.toJSON()])
        return JSONResponse(content=response.toJSON(), status_code=200)

    @handle_exceptions_controller
    async def delete(self, schedule_name):
        if not schedule_name:
            failed_response = FailedRequest(title="Error",
                                            description="Schedule name is required")
            return JSONResponse(content=failed_response.toJSON(), status_code=400)

        payload = await scheduleService.delete(schedule_name=schedule_name)

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        msg = Message(title='Delete schedule',
                      description=f"Schedule {schedule_name} deleted request done!",
                      type='INFO')
        response = SuccessfulRequest(messages=[msg.toJSON()])
        return JSONResponse(content=response.toJSON(), status_code=200)

    @handle_exceptions_controller
    async def update(self, info):

        if not info['values']['name'] or info['values']['name'] == '':
            failed_response = FailedRequest(title="Error",
                                            description="Schedule name is required")
            return JSONResponse(content=failed_response.toJSON(), status_code=400)

        payload = await k8s.update_velero_schedule(new_data=info['values'])

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        msg = Message(title='Schedule',
                      description=f"Schedule '{info['values']['name']}' successfully updated.",
                      type='INFO')
        response = SuccessfulRequest(messages=[msg.toJSON()])
        return JSONResponse(content=response.toJSON(), status_code=200)

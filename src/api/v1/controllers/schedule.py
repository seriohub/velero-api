from fastapi.responses import JSONResponse

from utils.handle_exceptions import handle_exceptions_controller

from api.common.response_model.failed_request import FailedRequest
from api.common.response_model.successful_request import SuccessfulRequest
from api.common.response_model.message import Message

from service.schedule_service import ScheduleService


from api.v1.schemas.create_schedule import CreateSchedule
from api.v1.schemas.delete_schedule import DeleteSchedule
from api.v1.schemas.update_schedule import UpdateSchedule
from api.v1.schemas.pause_unpause_schedule import PauseUnpauseSchedule

scheduleService = ScheduleService()


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
    async def pause(self, schedule: PauseUnpauseSchedule):
        if not schedule.name:
            failed_response = FailedRequest(title="Error",
                                            description="Schedule name is required")
            return JSONResponse(content=failed_response.toJSON(), status_code=400)

        payload = await scheduleService.pause(schedule_name=schedule.name)

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        msg = Message(title='Pause schedule',
                      description=f"Schedule {schedule.name} pause request done!",
                      type='INFO')
        response = SuccessfulRequest(notifications=[msg.toJSON()])
        return JSONResponse(content=response.toJSON(), status_code=200)

    @handle_exceptions_controller
    async def unpause(self, schedule: PauseUnpauseSchedule):
        if not schedule.name:
            failed_response = FailedRequest(title="Error",
                                            description="Schedule name is required")
            return JSONResponse(content=failed_response.toJSON(), status_code=400)

        payload = await scheduleService.unpause(schedule_name=schedule.name)

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        msg = Message(title='Pause schedule',
                      description=f"Schedule {schedule.name} start request done!",
                      type='INFO')
        response = SuccessfulRequest(notifications=[msg.toJSON()])
        return JSONResponse(content=response.toJSON(), status_code=200)

    @handle_exceptions_controller
    async def create(self, info: CreateSchedule):
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
        response = SuccessfulRequest(notifications=[msg.toJSON()])
        return JSONResponse(content=response.toJSON(), status_code=200)

    @handle_exceptions_controller
    async def delete(self, delete_schedule: DeleteSchedule):
        if not delete_schedule.resourceName:
            failed_response = FailedRequest(title="Error",
                                            description="Schedule name is required")
            return JSONResponse(content=failed_response.toJSON(), status_code=400)

        payload = await scheduleService.delete(schedule_name=delete_schedule.resourceName)

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        msg = Message(title='Delete schedule',
                      description=f"Schedule {delete_schedule.resourceName} deleted request done!",
                      type='INFO')
        response = SuccessfulRequest(notifications=[msg.toJSON()])
        return JSONResponse(content=response.toJSON(), status_code=200)

    @handle_exceptions_controller
    async def update(self, update_schedule: UpdateSchedule):

        if not update_schedule.name or update_schedule.name == '':
            failed_response = FailedRequest(title="Error",
                                            description="Schedule name is required")
            return JSONResponse(content=failed_response.toJSON(), status_code=400)

        payload = await scheduleService.update(new_data=update_schedule)

        if not payload['success']:
            response = FailedRequest(**payload['error'])
            return JSONResponse(content=response.toJSON(), status_code=400)

        msg = Message(title='Schedule',
                      description=f"Schedule '{update_schedule.name}' successfully updated.",
                      type='INFO')
        response = SuccessfulRequest(notifications=[msg.toJSON()])
        return JSONResponse(content=response.toJSON(), status_code=200)

    # async def get_manifest(self, schedule_name=None):
    #     payload = await scheduleService.get_manifest(schedule_name)
    #
    #     if not payload['success']:
    #         response = FailedRequest(**payload['error'])
    #         return JSONResponse(content=response.toJSON(), status_code=400)
    #
    #     response = SuccessfulRequest(payload=payload['data'])
    #     return JSONResponse(content=response.toJSON(), status_code=200)

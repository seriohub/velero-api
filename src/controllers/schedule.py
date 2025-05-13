# import json

from fastapi.responses import JSONResponse

from vui_common.schemas.response.successful_request import SuccessfulRequest
from vui_common.schemas.notification import Notification
from schemas.request.create_schedule import CreateScheduleRequestSchema
from schemas.request.update_schedule import UpdateScheduleRequestSchema
from schemas.response.successful_schedules import SuccessfulScheduleResponse

from service.schedule import (get_schedules_service,
                              delete_schedule_service,
                              create_schedule_service,
                              pause_schedule_service,
                              update_schedule_service)
from vui_common.logger.logger_proxy import logger


async def get_schedules_handler():
    print("30")
    payload = await get_schedules_service()

    response = SuccessfulScheduleResponse(payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=200)


async def pause_schedule_handler(schedule: str):
    logger.info(f"Sert schedule pause=True")
    payload = await pause_schedule_service(schedule)
    msg = Notification(title='Pause schedule',
                       description=f"Schedule {schedule} pause request done!",
                       type_='INFO')
    response = SuccessfulRequest(notifications=[msg], payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=200)


async def unpause_schedule_handler(schedule: str):
    payload = await pause_schedule_service(schedule_name=schedule, paused=False)

    msg = Notification(title='Pause schedule',
                       description=f"Schedule {schedule} start request done!",
                       type_='INFO')
    response = SuccessfulRequest(notifications=[msg], payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=200)


async def create_schedule_handler(info: CreateScheduleRequestSchema):
    payload = await create_schedule_service(schedule_data=info)

    msg = Notification(title='Create schedule',
                       description=f"Schedule {info.name} created!",
                       type_='INFO')
    response = SuccessfulRequest(notifications=[msg], payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=200)


async def delete_schedule_handler(schedule_name: str):
    payload = await delete_schedule_service(schedule_name=schedule_name)

    msg = Notification(title='Delete schedule',
                       description=f"Schedule {schedule_name} deleted request done!",
                       type_='INFO')
    response = SuccessfulRequest(notifications=[msg], payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=200)


async def update_schedule_handler(schedule: UpdateScheduleRequestSchema):
    payload = await update_schedule_service(schedule_data=schedule)

    msg = Notification(title='Schedule',
                       description=f"Schedule '{schedule.name}' successfully updated.",
                       type_='INFO')
    response = SuccessfulRequest(notifications=[msg], payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=200)

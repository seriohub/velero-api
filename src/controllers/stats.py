from fastapi.responses import JSONResponse

from schemas.response.successful_request import SuccessfulRequest

from service.stats import get_stats_service, get_in_progress_task_service, get_schedules_heatmap_service


async def get_stats_handler():
    payload = await get_stats_service()

    response = SuccessfulRequest(payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=200)


async def get_in_progress_task_handler():
    payload = await get_in_progress_task_service()

    response = SuccessfulRequest(payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=200)


async def get_schedules_heatmap_handler():
    payload = await get_schedules_heatmap_service()

    response = SuccessfulRequest(payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=200)

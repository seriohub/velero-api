from fastapi.responses import JSONResponse

from schemas.response.successful_request import SuccessfulRequest

from service.backup import get_backups_service
from service.restore import get_restores_service
from service.stats import get_stats_service
from service.schedule_heatmap import get_schedules_heatmap_service


async def get_stats_handler():
    payload = await get_stats_service()

    response = SuccessfulRequest(payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=200)


async def get_in_progress_task_handler():
    backups = await get_backups_service(in_progress=True)
    restores = await get_restores_service(in_progress=True)
    payload = [*backups, *restores]

    response = SuccessfulRequest(payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=200)


async def get_schedules_heatmap_handler():
    payload = await get_schedules_heatmap_service()

    response = SuccessfulRequest(payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=200)

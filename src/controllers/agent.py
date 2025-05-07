from fastapi.responses import JSONResponse

from vui_common.schemas.response.successful_request import SuccessfulRequest

from service.watchdog import check_watchdog_online_service


async def watchdog_online_handler():
    payload = await check_watchdog_online_service()

    response = SuccessfulRequest(payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=200)

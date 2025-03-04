from fastapi.responses import JSONResponse

from schemas.response.successful_request import SuccessfulRequest

from service.k8s import get_k8s_online_service


async def get_k8s_online_handler():
    payload = await get_k8s_online_service()

    response = SuccessfulRequest(payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=200)

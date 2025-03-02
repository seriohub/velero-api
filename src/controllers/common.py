from fastapi.responses import JSONResponse

from schemas.response.successful_request import SuccessfulRequest

from utils.commons import logs_string_to_list

from service.logs import get_velero_logs_service
from service.describe import get_velero_resource_details_service


async def get_resource_describe_handler(resource_name: str, resource_type: str):
    payload = await get_velero_resource_details_service(resource_name, resource_type)

    response = SuccessfulRequest(payload=payload.details)
    return JSONResponse(content=response.model_dump(), status_code=200)


async def get_resource_logs_handler(resource_name: str, resource_type: str):
    payload = await get_velero_logs_service(resource_name, resource_type)

    logs = payload.logs

    data = logs_string_to_list('\n'.join(logs))

    response = SuccessfulRequest(payload={'text': logs, 'table': data})
    return JSONResponse(content=response.model_dump(), status_code=200)

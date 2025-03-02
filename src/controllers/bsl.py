from fastapi.responses import JSONResponse

from schemas.response.successful_request import SuccessfulRequest
from schemas.notification import Notification
from schemas.request.create_bsl import CreateBslRequestSchema
from schemas.request.default_bsl import DefaultBslRequestSchema

from service.bsl import (remove_default_bsl_service,
                         set_default_bsl_service,
                         create_bsl_service,
                         delete_bsl_service,
                         get_bsls_service)


async def get_bsls_handler():
    payload = await get_bsls_service()

    response = SuccessfulRequest(payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=200)


async def create_bsl_handler(bsl: CreateBslRequestSchema):
    payload = await create_bsl_service(bsl)

    msg = Notification(title='Create bsl', description=f"BSL {bsl.name} created!", type_='INFO')
    response = SuccessfulRequest(notifications=[msg], payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=201)


async def set_default_bsl_handler(default_bsl: DefaultBslRequestSchema):

    payload = await set_default_bsl_service(default_bsl.name)

    msg = Notification(title='Default bsl', description=f"BSL {default_bsl.name} set as default!", type_='INFO')
    response = SuccessfulRequest(notifications=[msg], payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=201)


async def set_remove_default_bsl_handler(default_bsl: DefaultBslRequestSchema):
    payload = await remove_default_bsl_service(default_bsl.name)

    msg = Notification(title='Default bsl', description=f"BSL {default_bsl.name} removed as default!", type_='INFO')
    response = SuccessfulRequest(notifications=[msg], payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=201)


async def delete_bsl_handler(bsl_name: str):
    payload = await delete_bsl_service(bsl_name=bsl_name)

    msg = Notification(title='Delete bsl',
                       description=f'Bsl {bsl_name} deleted request done!',
                       type_='INFO')

    response = SuccessfulRequest(payload=payload)
    response.notifications = [msg]
    return JSONResponse(content=response.model_dump(), status_code=200)

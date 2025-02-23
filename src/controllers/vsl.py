from fastapi.responses import JSONResponse

from schemas.response.successful_request import SuccessfulRequest
from schemas.notification import Notification
from schemas.request.create_vsl import CreateVslRequestSchema

from service.vsl import get_vsls_service, create_vsl_service, delete_vsl_service


async def get_vsl_handler():
    payload = await get_vsls_service()

    response = SuccessfulRequest(payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=200)


async def create_vsl_handler(create_bsl: CreateVslRequestSchema):
    payload = await create_vsl_service(create_bsl)

    msg = Notification(title='Create bsl', description=f"BSL {create_bsl.name} created!", type_='INFO')
    response = SuccessfulRequest(notifications=[msg], payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=201)


async def delete_vsl_handler(bsl_delete: str):
    payload = await delete_vsl_service(vsl_name=bsl_delete)

    msg = Notification(title='Delete bsl', description=f'Bsl {bsl_delete} deleted request done!', type_='INFO')

    response = SuccessfulRequest(msg=[msg], payload=payload)

    return JSONResponse(content=response.model_dump(), status_code=200)

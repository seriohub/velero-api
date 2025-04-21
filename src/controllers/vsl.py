from fastapi.responses import JSONResponse

from schemas.request.update_vsl import UpdateVslRequestSchema
from vui_common.schemas.response.successful_request import SuccessfulRequest
from vui_common.schemas.notification import Notification
from schemas.request.create_vsl import CreateVslRequestSchema

from service.vsl import get_vsls_service, create_vsl_service, delete_vsl_service, update_vsl_service


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
    response = SuccessfulRequest(notifications=[msg], payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=200)

async def update_vsl_handler(vsl: UpdateVslRequestSchema):
    payload = await update_vsl_service(vsl_data=vsl)

    msg = Notification(title='Vsl',
                       description=f"Vsl '{vsl.name}' successfully updated.",
                       type_='INFO')

    response = SuccessfulRequest(payload=payload, notifications=[msg])
    return JSONResponse(content=response.model_dump(), status_code=200)

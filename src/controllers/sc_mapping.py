from fastapi.responses import JSONResponse

from schemas.response.successful_request import SuccessfulRequest
from schemas.notification import Notification
from schemas.request.storage_class_map import StorageClassMapRequestSchema

from service.sc_mapping import (get_storages_classes_map_service,
                                update_storages_classes_mapping_service,
                                delete_storages_classes_mapping_service)


async def get_storages_classes_map_handler():
    payload = await get_storages_classes_map_service()

    response = SuccessfulRequest(payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=200)


async def update_storages_classes_mapping_handler(maps: StorageClassMapRequestSchema):
    payload = await update_storages_classes_mapping_service(data_list=maps.storageClassMapping)

    msg = Notification(title='Storage Class Map', description=f"Done!", type_='INFO')
    response = SuccessfulRequest(notifications=[msg], payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=200)


async def delete_storages_classes_mapping_handler(data_list=None):
    payload = await delete_storages_classes_mapping_service(data_list=data_list)

    msg = Notification(title='Storage Class Map', description=f"Deleted!", type_='INFO')
    response = SuccessfulRequest(notifications=[msg], payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=200)

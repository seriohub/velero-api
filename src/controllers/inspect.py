import os
from fastapi.responses import JSONResponse

from schemas.response.successful_request import SuccessfulRequest
from configs.config_boot import config_app
from service.inspect import (get_folders_list,
                             # get_directory_contents,
                             read_json_file,
                             get_recursive_directory_contents)


async def get_backups_handler():
    payload = await get_folders_list(config_app.app.inspect_folder)

    response = SuccessfulRequest(payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=200)


# async def get_folders_handler(path: str):
#     payload = await get_directory_contents(os.path.join(config_app.app.inspect_folder, path))
#
#     response = SuccessfulRequest(payload=payload)
#     return JSONResponse(content=response.model_dump(), status_code=200)
#

async def get_file_content_handler(path: str):
    payload = await read_json_file(os.path.join(config_app.app.inspect_folder, path))

    response = SuccessfulRequest(payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=200)


async def get_recursive_directory_contents_handler(backup: str):
    payload = await get_recursive_directory_contents(os.path.join(config_app.app.inspect_folder, backup))

    response = SuccessfulRequest(payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=200)

from fastapi.responses import JSONResponse

from schemas.response.successful_request import SuccessfulRequest

from database.db_connection import SessionLocal

from configs.config_boot import config_app

from service.info import identify_architecture_service, ui_compatibility_service, last_tags_from_github_service


async def identify_architecture_handler():
    payload = await identify_architecture_service()

    response = SuccessfulRequest(payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=200)


async def get_origins_handler():
    payload = config_app.get_origins()

    response = SuccessfulRequest(payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=200)


async def last_tags_from_github_handler(force_refresh: bool, db: SessionLocal):
    payload = await last_tags_from_github_service(db,
                                                  force_refresh=force_refresh,
                                                  check_version=True)

    response = SuccessfulRequest(payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=200)


async def last_tag_velero_from_github_handler(force_refresh: bool, db: SessionLocal):
    payload = await last_tags_from_github_service(db,
                                                  force_refresh=force_refresh,
                                                  check_version=True,
                                                  only_velero=True)

    response = SuccessfulRequest(payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=200)


async def ui_compatibility_handler(version):
    payload = await ui_compatibility_service(version)

    response = SuccessfulRequest(payload=payload)
    return JSONResponse(content=response.model_dump(), status_code=200)

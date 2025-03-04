from fastapi import APIRouter

from api.common.routers import info

appInfo = APIRouter()

appInfo.include_router(info.router)


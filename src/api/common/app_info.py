from fastapi import APIRouter

from api.common.routers import info, agent

appInfo = APIRouter()

# appInfo.include_router(health.router)
appInfo.include_router(info.router)
appInfo.include_router(agent.router)

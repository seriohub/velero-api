from fastapi import APIRouter
from api.common.routers import health

appAgentHealth = APIRouter()
appAgentHealth.include_router(health.router)

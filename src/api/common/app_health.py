from fastapi import APIRouter
from api.common.routers import health


appHealth = APIRouter()
appHealth.include_router(health.router)

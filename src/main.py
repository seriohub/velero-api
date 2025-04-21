from fastapi import FastAPI
from contextlib import asynccontextmanager

from vui_common.app import create_base_app

from api.common.app_health import appAgentHealth
from api.v1.api_v1 import v1

from startup_watchers import init_watchers


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_watchers(app)
    yield


app = create_base_app(component='agent', lifespan=lifespan)

app.include_router(appAgentHealth, prefix="/health")
app.include_router(v1, prefix="/v1")

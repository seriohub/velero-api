import os
from dotenv import load_dotenv
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app_settings import *
from routers import backup_v1
from routers import restore_v1
from routers import schedule_v1
from routers import utils_v1
from routers import k8s_v1
from routers import repo_v1
from routers import backup_location_v1
from routers import snapshot_location_v1

load_dotenv()
app = FastAPI()

# origins = [
#    "http://localhost:3000",
#    "http://127.0.0.1:3000",
# ]

origins = json.loads(os.environ['ORIGINS'])

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(backup_v1.router, prefix="/api/v1")
app.include_router(restore_v1.router, prefix="/api/v1")
app.include_router(schedule_v1.router, prefix="/api/v1")
app.include_router(utils_v1.router, prefix="/api/v1")
app.include_router(k8s_v1.router, prefix="/api/v1")
app.include_router(repo_v1.router, prefix="/api/v1")
app.include_router(backup_location_v1.router, prefix="/api/v1")
app.include_router(snapshot_location_v1.router, prefix="/api/v1")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    await manager.send_personal_message("Connection READY!", websocket=websocket)

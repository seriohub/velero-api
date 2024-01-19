import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
import json
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from connection_manager import *
from helpers.printer_helper import PrintHelper
from libs.config import ConfigEnv


from libs.security.middleware import add_process_time_header
from routers import backup, app_info
from routers import restore
from routers import schedule
from routers import utils
from routers import k8s
from routers import repo
from routers import backup_location
from routers import snapshot_location
from routers import authentications

from utils.app_data import __version__, __app_name__, __app_description__, __app_summary__
from libs.security.users import get_current_active_user, create_default_user, SessionLocal

load_dotenv()
config = ConfigEnv()

# init logger engine
print_helper = PrintHelper('app')

docs_url = '/docs'
re_docs_url = '/redocs'

# if not config_app.get_api_disable_documentation():
disable_docs = False
if disable_docs:
    docs_url = None
    re_docs_url = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = SessionLocal()
    try:
        # Create default db
        create_default_user(db)
        yield db

    finally:
        db.close()
    yield


app = FastAPI(
    title=__app_name__,
    description=__app_description__,
    summary=__app_summary__,
    version=__version__,
    license_info={
        'name': 'Apache 2.0',
        'identifier': 'Apache-2.0',
    },
    docs_url=docs_url,
    redoc_url=re_docs_url,
    lifespan=lifespan
)

origins = json.loads(os.environ['ORIGINS'])

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.middleware('http')(add_process_time_header)

app.include_router(authentications.router,
                   prefix='/api/v1')
app.include_router(app_info.router,
                   prefix='/api/v1')

app.include_router(backup.router,
                   dependencies=[Depends(get_current_active_user)],
                   prefix='/api/v1')
app.include_router(restore.router,
                   dependencies=[Depends(get_current_active_user)],
                   prefix='/api/v1')
app.include_router(schedule.router,
                   dependencies=[Depends(get_current_active_user)],
                   prefix='/api/v1')
app.include_router(utils.router,
                   dependencies=[Depends(get_current_active_user)],
                   prefix='/api/v1')
app.include_router(k8s.router,
                   dependencies=[Depends(get_current_active_user)],
                   prefix='/api/v1')
app.include_router(repo.router,
                   dependencies=[Depends(get_current_active_user)],
                   prefix='/api/v1')
app.include_router(backup_location.router,
                   dependencies=[Depends(get_current_active_user)],
                   prefix='/api/v1')
app.include_router(snapshot_location.router,
                   dependencies=[Depends(get_current_active_user)],
                   prefix='/api/v1')


# @app.websocket("/ws",
#                dependencies=[Depends(get_current_active_user)])
# Can't use jwt in socket header request
@app.websocket('/ws')
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    await manager.send_personal_message('Connection READY!', websocket=websocket)

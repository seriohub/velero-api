from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from connection_manager import *
from helpers.printer_helper import PrintHelper
from libs.config import ConfigEnv
from fastapi.responses import JSONResponse


from libs.security.middleware import add_process_time_header
from app_info import appInfo

from utils.app_data import __version__, __app_name__, __app_description__, __app_summary__
from libs.security.users import create_default_user, SessionLocal
from v1 import v1


load_dotenv()
config = ConfigEnv()

# init logger engine
print_helper = PrintHelper('app')

# docs redocs
docs_url = '/docs'
re_docs_url = '/redoc'
enabled_docs = config.get_api_disable_documentation()
if not enabled_docs:
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

origins = config.get_origins()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.middleware('http')(add_process_time_header)


@app.get('/')
async def online():
    return JSONResponse(content={'status': 'alive'}, status_code=200)


# @app.websocket("/ws",
#                dependencies=[Depends(get_current_active_user)])
# Can't use jwt in socket header request
@app.websocket('/ws')
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    await manager.send_personal_message('Connection READY!', websocket=websocket)


app.mount("/api/v1", v1, "v1")
app.mount("/info", appInfo, "appInfo")

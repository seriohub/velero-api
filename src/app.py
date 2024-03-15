from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from helpers.connection_manager import WebSocket, manager
# from helpers.printer import PrintHelper
from core.config import ConfigHelper
from fastapi.responses import JSONResponse


from security.middleware import add_process_time_header
from api.common.app_info import appInfo

from app_data import __version__, __app_name__, __app_description__, __app_summary__
from security.users import create_default_user, SessionLocal
from api.v1.api_v1 import v1

load_dotenv()
config = ConfigHelper()

# init logger engine
# print_helper = PrintHelper('[app]')

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
    expose_headers=["X-Process-Time"]
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
    # await manager.send_personal_message('Connection READY!', websocket=websocket)


app.mount("/api/v1", v1, "v1")
app.mount("/info", appInfo, "appInfo")

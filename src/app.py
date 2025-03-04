from dotenv import load_dotenv

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from ws.websocket_manager import WebSocket, manager

from contexts.context import called_endpoint_var

from security.middleware.middleware import add_process_time_header

from api.common.app_info import appInfo
from api.common.app_health import appHealth

from api.v1.api_v1 import v1

from app_data import __version__, __app_name__, __app_description__, __app_summary__
from configs.config_boot import config_app

load_dotenv()

# docs redocs
docs_url = '/docs'
re_docs_url = '/redoc'
enabled_docs = config_app.app.swagger_documentation_disabled
if not enabled_docs:
    docs_url = None
    re_docs_url = None

app = FastAPI(root_path="/api",  # if not config.get_developer_mode() else '/',
              title=__app_name__,
              description=__app_description__,
              summary=__app_summary__,
              version=__version__,
              license_info={'name': 'Apache 2.0', 'identifier': 'Apache-2.0', },
              docs_url=docs_url,
              redoc_url=re_docs_url,

              )

origins = config_app.security.get_origins()

app.add_middleware(CORSMiddleware,
                   allow_origins=origins,
                   allow_credentials=True,
                   allow_methods=['*'],
                   allow_headers=['*'],
                   expose_headers=["X-Process-Time"])

app.middleware('http')(add_process_time_header)


@app.middleware("http")
async def set_called_endpoint(request: Request, call_next):
    # get the endpoint called by the request
    called_endpoint = request.url.path
    # set the endpoint called in the context variable
    ce = called_endpoint_var.set(called_endpoint)
    try:
        # call the next endpoint in the application
        return await call_next(request)
    finally:
        called_endpoint_var.reset(ce)


@app.get('/online')
@app.get('/')
async def online():
    return JSONResponse(
        content={'data': {'status': 'alive', 'type': 'agent', 'cluster_id': config_app.k8s.cluster_id}},
        status_code=200)


# @app.websocket("/ws",
#                dependencies=[Depends(get_current_active_user)])
# Can't use jwt in socket header request
@app.websocket('/ws/auth')
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)


@app.websocket('/ws/online')
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()


app.include_router(appHealth, prefix="/health")

app.include_router(appInfo, prefix="/info")

app.include_router(v1, prefix="/v1")

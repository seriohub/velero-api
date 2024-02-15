from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from helpers.printer_helper import PrintHelper
from libs.config import ConfigEnv
from fastapi.responses import JSONResponse


from routers import backup, app_info
from routers import restore
from routers import schedule
from routers import utils
from routers import k8s
from routers import repo
from routers import backup_location
from routers import snapshot_location
from routers import authentications
from routers import sc_mapping

from utils.app_data import __version__, __app_name__, __app_description__, __app_summary__
from libs.security.users import get_current_active_user

load_dotenv()
config = ConfigEnv()

# init logger engine
print_helper = PrintHelper('app')

# docs redoc
docs_url = '/docs'
re_docs_url = '/redoc'
enabled_docs = config.get_api_disable_documentation()
if not enabled_docs:
    docs_url = None
    re_docs_url = None


v1 = FastAPI(
    title=__app_name__,
    description=__app_description__,
    summary=__app_summary__,
    version=__version__,
    license_info={
        'name': 'Apache 2.0',
        'identifier': 'Apache-2.0',
    },
    docs_url=docs_url,
    redoc_url=re_docs_url
)


@v1.get('/')
# @app.docsOnlyLoggedIn
async def online():
    return JSONResponse(content={'v1': 'alive'}, status_code=200)

v1.include_router(authentications.router)

v1.include_router(backup.router,
                  dependencies=[Depends(get_current_active_user)])
v1.include_router(restore.router,
                  dependencies=[Depends(get_current_active_user)])
v1.include_router(schedule.router,
                  dependencies=[Depends(get_current_active_user)])
v1.include_router(utils.router,
                  dependencies=[Depends(get_current_active_user)])
v1.include_router(k8s.router,
                  dependencies=[Depends(get_current_active_user)])
v1.include_router(repo.router,
                  dependencies=[Depends(get_current_active_user)])
v1.include_router(backup_location.router,
                  dependencies=[Depends(get_current_active_user)])
v1.include_router(snapshot_location.router,
                  dependencies=[Depends(get_current_active_user)])
v1.include_router(sc_mapping.router,
                  dependencies=[Depends(get_current_active_user)])

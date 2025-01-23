# from dotenv import load_dotenv
from fastapi import FastAPI, Depends, APIRouter
# from helpers.printer import PrintHelper
# from core.config import ConfigHelper
# from fastapi.responses import JSONResponse

from api.v1.routers import (sc_mapping,
                            repo,
                            restore,
                            stats,
                            k8s,
                            snapshot_location,
                            backup,
                            schedule,
                            backup_location,
                            setup,
                            watchdog,
                            pod_volume_backup)
from security.routers import authentication, user

# from app_data import __version__, __app_name__, __app_description__, __app_summary__
from security.service.helpers.users import get_current_active_user


# load_dotenv()
# config = ConfigHelper()
#
# # init logger engine
# # print_helper = PrintHelper('[app]')
#
#
# # docs redoc
# docs_url = '/docs'
# re_docs_url = '/redoc'
# enabled_docs = config.get_api_disable_documentation()
# if not enabled_docs:
#     docs_url = None
#     re_docs_url = None
#
#
# v1 = FastAPI(
#     title=__app_name__,
#     description=__app_description__,
#     summary=__app_summary__,
#     version=__version__,
#     license_info={
#         'name': 'Apache 2.0',
#         'identifier': 'Apache-2.0',
#     },
#     docs_url=docs_url,
#     redoc_url=re_docs_url
# )

v1 = APIRouter()

# @v1.get('/')
# # @app.docsOnlyLoggedIn
# async def online():
#     return JSONResponse(content={'v1': 'alive'}, status_code=200)

v1.include_router(authentication.router)

v1.include_router(user.router,
                  dependencies=[Depends(get_current_active_user)])
v1.include_router(backup.router,
                  dependencies=[Depends(get_current_active_user)])
v1.include_router(restore.router,
                  dependencies=[Depends(get_current_active_user)])
v1.include_router(schedule.router,
                  dependencies=[Depends(get_current_active_user)])
v1.include_router(setup.router,
                  dependencies=[Depends(get_current_active_user)])
v1.include_router(k8s.router,
                  dependencies=[Depends(get_current_active_user)])
v1.include_router(repo.router,
                  dependencies=[Depends(get_current_active_user)])
v1.include_router(backup_location.router,
                  dependencies=[Depends(get_current_active_user)])
v1.include_router(snapshot_location.router,
                  dependencies=[Depends(get_current_active_user)])
v1.include_router(pod_volume_backup.router,
                  dependencies=[Depends(get_current_active_user)])
v1.include_router(sc_mapping.router,
                  dependencies=[Depends(get_current_active_user)])
v1.include_router(stats.router,
                  dependencies=[Depends(get_current_active_user)])
v1.include_router(watchdog.router,
                  dependencies=[Depends(get_current_active_user)])

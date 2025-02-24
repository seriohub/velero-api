from fastapi import Depends, APIRouter

from api.v1.routers import (sc_mapping,
                            repo,
                            restore,
                            stats,
                            k8s,
                            vsl,
                            backup,
                            schedule,
                            bsl,
                            setup,
                            watchdog,
                            pvb,
                            location)
from security.routers import authentication, user
from security.authentication.auth_service import get_current_active_user

from configs.config_boot import config_app


v1 = APIRouter()

if config_app.app.auth_enabled:

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
    v1.include_router(bsl.router,
                      dependencies=[Depends(get_current_active_user)])
    v1.include_router(vsl.router,
                      dependencies=[Depends(get_current_active_user)])
    v1.include_router(pvb.router,
                      dependencies=[Depends(get_current_active_user)])
    v1.include_router(sc_mapping.router,
                      dependencies=[Depends(get_current_active_user)])
    v1.include_router(stats.router,
                      dependencies=[Depends(get_current_active_user)])
    v1.include_router(watchdog.router,
                      dependencies=[Depends(get_current_active_user)])
    v1.include_router(location.router,
                      dependencies=[Depends(get_current_active_user)])

else:
    v1.include_router(backup.router)
    v1.include_router(restore.router)
    v1.include_router(schedule.router)
    v1.include_router(setup.router)
    v1.include_router(k8s.router)
    v1.include_router(repo.router)
    v1.include_router(bsl.router)
    v1.include_router(vsl.router)
    v1.include_router(pvb.router)
    v1.include_router(sc_mapping.router)
    v1.include_router(stats.router)
    v1.include_router(watchdog.router)
    v1.include_router(location.router)

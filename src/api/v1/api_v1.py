from fastapi import Depends, APIRouter

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

from security.service.helpers.users import get_current_active_user

v1 = APIRouter()

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

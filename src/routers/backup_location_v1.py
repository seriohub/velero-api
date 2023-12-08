from fastapi import APIRouter

from helpers.handle_exceptions import *
from libs.backup_location_v1 import BackupLocationV1

router = APIRouter()

backupLocation = BackupLocationV1()


@router.get('/backup-location/get')
@handle_exceptions_async_method
async def get():
    return await backupLocation.get()

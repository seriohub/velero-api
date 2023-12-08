from fastapi import APIRouter

from helpers.handle_exceptions import *
from libs.snapshot_location_v1 import SnapshotLocationV1

router = APIRouter()

snapshotLocation = SnapshotLocationV1()


@router.get('/snapshot-location/get')
@handle_exceptions_async_method
async def get():
    return await snapshotLocation.get()

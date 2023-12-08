from fastapi import APIRouter

from helpers.handle_exceptions import *
from libs.utils_v1 import UtilsV1

router = APIRouter()

utils = UtilsV1()


@router.get('/utils/stats')
@handle_exceptions_async_method
async def stats():
    return await utils.stats()


@router.get('/utils/version')
@handle_exceptions_async_method
async def version():
    return await utils.version()


@router.get('/utils/in-progress')
@handle_exceptions_async_method
async def in_progress():
    return await utils.in_progress()

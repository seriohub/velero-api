from fastapi import APIRouter

from helpers.handle_exceptions import *
from libs.repo_v1 import RepoV1

router = APIRouter()

repo = RepoV1()


@router.get('/repo/get')
@handle_exceptions_async_method
async def get():
    return await repo.get()

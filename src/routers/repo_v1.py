from fastapi import APIRouter, Depends
from helpers.handle_exceptions import *
from helpers.printer_helper import PrintHelper

from libs.repo_v1 import RepoV1
from libs.security.rate_limiter import RateLimiter, LimiterRequests


router = APIRouter()
repo = RepoV1()
print_ls = PrintHelper('routes.repo_v1')

endpoint_limiter = LimiterRequests(debug=False,
                                   printer=print_ls,
                                   tags="Backup",
                                   default_key='L1')
limiter = endpoint_limiter.get_limiter_cust("repo_get")


@router.get('/repo/get',
            tags=["Repository"],
            summary="Get backups repository",
            dependencies=[Depends(RateLimiter(interval_seconds=limiter.seconds,
                                              max_requests=limiter.max_request))]
            )
@handle_exceptions_async_method
async def get():
    return await repo.get()

from typing import Annotated
from fastapi import APIRouter, Depends
from security.schemas.request.OAuth2_request import OAuth2PasswordAndRefreshRequestForm
from typing import Union
from security.controllers.authentication import Authentication
from security.schemas.response.token import TokenRefresh, Token
from security.helpers.rate_limiter import LimiterRequests, RateLimiter

from utils.commons import route_description

from core.config import ConfigHelper

config = ConfigHelper()
router = APIRouter()

auth = Authentication()

tag_name = 'Security'
endpoint_limiter = LimiterRequests(tags=tag_name,
                                   default_key='L1')

limiter = endpoint_limiter.get_limiter_cust('token')
route = '/token'


@router.post(path=route,
             tags=[tag_name],
             summary='Release a new token',
             description=route_description(tag=tag_name,
                                           route=route,
                                           limiter_calls=limiter.max_request,
                                           limiter_seconds=limiter.seconds),
             dependencies=[Depends(RateLimiter(interval_seconds=limiter.seconds,
                                               max_requests=limiter.max_request))],
             response_model=Union[Token, TokenRefresh])
async def login_for_access_token(form_data: Annotated[OAuth2PasswordAndRefreshRequestForm, Depends()]):
    if form_data.grant_type == "refresh_token":
        return await auth.refresh_login(form_data.refresh_token)
    else:
        return await auth.login(form_data.username, form_data.password)

# limiter_tr = endpoint_limiter.get_limiter_cust('token_refresh')
# route = '/token-refresh'
#
#
# @router.post(path=route,
#              tags=[tag_name],
#              summary='Refresh the access token',
#              description=route_description(tag=tag_name,
#                                            route=route,
#                                            limiter_calls=limiter_tr.max_request,
#                                            limiter_seconds=limiter_tr.seconds),
#              dependencies=[Depends(RateLimiter(interval_seconds=limiter_tr.seconds,
#                                                max_requests=limiter_tr.max_request))],
#              response_model=TokenRefresh)
# async def refresh_access_token(refresh_token: str, db: Session = Depends(get_db)):
#     return await auth.refresh_login(refresh_token, db)

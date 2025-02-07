from fastapi import APIRouter
from fastapi.responses import JSONResponse

from security.model.model import UserUPDPassword
from security.service.helpers.rate_limiter import LimiterRequests, RateLimiter
from security.service.helpers.users import *

from utils.commons import route_description

from core.config import ConfigHelper

config = ConfigHelper()
router = APIRouter()
token_expires_minutes = config.get_security_token_expiration()
token_expires_days = config.get_security_token_refresh_expiration()

enable_users = config.get_security_manage_users()

tag_name = 'User'
endpoint_limiter = LimiterRequests(tags=tag_name,
                                   default_key='L1')

limiter_me_info = endpoint_limiter.get_limiter_cust('users_me_info')
route = '/users/me/info'


@router.get(path=route,
            tags=[tag_name],
            summary='Get information about the user authenticated',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter_me_info.max_request,
                                          limiter_seconds=limiter_me_info.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_me_info.seconds,
                                              max_requests=limiter_me_info.max_request))],
            response_model=UserOut)
async def read_current_user(current_user: User = Depends(get_current_active_user)):
    return JSONResponse(content={'data': current_user.toJSON()}, status_code=201)


limiter_me_pwd = endpoint_limiter.get_limiter_cust('users_me_pwd')
route = '/users/me/update/pwd'


@router.put(path=route,
            tags=[tag_name],
            summary='Update user password',
            description=route_description(tag=tag_name,
                                          route=route,
                                          limiter_calls=limiter_me_pwd.max_request,
                                          limiter_seconds=limiter_me_pwd.seconds),
            dependencies=[Depends(RateLimiter(interval_seconds=limiter_me_pwd.seconds,
                                              max_requests=limiter_me_pwd.max_request))], )
def update_current_user(user: UserUPDPassword,
                        current_user: User = Depends(get_current_active_user),
                        db: Session = Depends(get_db)):
    return update_user(user_id=current_user.id,
                       full_name='',
                       password=user.password,
                       db=db)


if enable_users:
    # Routes for user management

    limiter_add = endpoint_limiter.get_limiter_cust('users_create')
    route = '/users/create'


    @router.post(path=route,
                 tags=[tag_name],
                 summary='Create new user',
                 description=route_description(tag=tag_name,
                                               route=route,
                                               limiter_calls=limiter_add.max_request,
                                               limiter_seconds=limiter_add.seconds),
                 dependencies=[Depends(RateLimiter(interval_seconds=limiter_add.seconds,
                                                   max_requests=limiter_add.max_request))],
                 response_model=UserOut)
    def create_new_user(user: UserCreate,
                        current_user: User = Depends(get_current_active_user),
                        db: Session = Depends(get_db)):
        if current_user.is_admin:
            return create_user(user=user,
                               db=db)
        else:
            raise HTTPException(status_code=403,
                                detail='You are not authorized.Permission denied')


    limiter_us = endpoint_limiter.get_limiter_cust('users')
    route = '/users/'


    @router.get(path=route,
                tags=[tag_name],
                summary='Get all user registered',
                description=route_description(tag=tag_name,
                                              route=route,
                                              limiter_calls=limiter_us.max_request,
                                              limiter_seconds=limiter_us.seconds),
                dependencies=[Depends(RateLimiter(interval_seconds=limiter_us.seconds,
                                                  max_requests=limiter_us.max_request))],
                response_model=List[UserOut])
    def read_users(db: Session = Depends(get_db)):
        return get_all_users(db)


    limiter_uid = endpoint_limiter.get_limiter_cust('users_user_id')
    route = '/users/{user_id}'


    @router.get(path=route,
                tags=[tag_name],
                summary='Get user data',
                description=route_description(tag=tag_name,
                                              route=route,
                                              limiter_calls=limiter_uid.max_request,
                                              limiter_seconds=limiter_uid.seconds),
                dependencies=[Depends(RateLimiter(interval_seconds=limiter_uid.seconds,
                                                  max_requests=limiter_uid.max_request))],
                response_model=UserOut)
    def read_user(user_id: uuid.UUID, db: Session = Depends(get_db)):
        user = get_user(user_id=user_id,
                        db=db)
        if user is None:
            raise HTTPException(status_code=404, detail='User not found')
        return user


    limiter_del_id = endpoint_limiter.get_limiter_cust('users_user_id_delete')
    route = '/users/{user_id}/delete'


    @router.delete(path=route,
                   tags=[tag_name],
                   summary='Delete user',
                   description=route_description(tag=tag_name,
                                                 route=route,
                                                 limiter_calls=limiter_del_id.max_request,
                                                 limiter_seconds=limiter_del_id.seconds),
                   dependencies=[Depends(RateLimiter(interval_seconds=limiter_del_id.seconds,
                                                     max_requests=limiter_del_id.max_request))], )
    def delete_existing_user(user_id: uuid.UUID,
                             current_user: User = Depends(get_current_active_user),
                             db: Session = Depends(get_db)):
        if current_user.is_admin:
            return delete_user(user_id=user_id,
                               db=db)
        else:
            raise HTTPException(status_code=403,
                                detail='You are not authorized. Permission denied')


    limiter_udis = endpoint_limiter.get_limiter_cust('users_user_id_disable')
    route = '/users/{user_id}/disable'


    @router.put(path=route,
                tags=[tag_name],
                summary='Disable user',
                description=route_description(tag=tag_name,
                                              route=route,
                                              limiter_calls=limiter_udis.max_request,
                                              limiter_seconds=limiter_udis.seconds),
                dependencies=[Depends(RateLimiter(interval_seconds=limiter_udis.seconds,
                                                  max_requests=limiter_udis.max_request))], )
    def disable_existing_user(user_id: uuid.UUID,
                              current_user: User = Depends(get_current_active_user),
                              db: Session = Depends(get_db)):
        if current_user.is_admin:
            return disable_user(user_id=user_id,
                                db=db)
        else:
            raise HTTPException(status_code=403,
                                detail='You are not authorized.Permission denied')

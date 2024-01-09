from typing import Annotated
from fastapi import Request
from fastapi import APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from libs.security.model import Token, UserUPDPassword
from libs.security.rate_limiter import LimiterRequests, RateLimiter
from libs.security.users import *
from helpers.printer_helper import PrintHelper
from libs.config import ConfigEnv


config = ConfigEnv()
token_expires_minutes = config.get_security_token_expiration()
print_ls = PrintHelper('routes.authentication')

endpoint_limiter = LimiterRequests(debug=False,
                                   printer=print_ls,
                                   tags="Security",
                                   default_key='L1')

limiter = endpoint_limiter.get_limiter_cust("token")

enable_users = config.get_security_manage_users()

router = APIRouter()


@router.post("/token",
             tags=["Security"],
             summary="Release o renew token",
             dependencies=[Depends(RateLimiter(interval_seconds=limiter.seconds,
                                               max_requests=limiter.max_request))],
             response_model=Token)
async def login_for_access_token(request: Request,
                                 form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: Session = Depends(get_db)):
    print_ls.info(f"User:{form_data.username}-Password:{form_data.password[:2]}**")
    if len(form_data.username)>1 and len(form_data.password)>1:
        user = authenticate_user(db=db,
                                 username=form_data.username,
                                 password=form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token_expires = timedelta(minutes=token_expires_minutes)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username o password not passed",
            headers={"WWW-Authenticate": "Bearer"},
        )


limiter = endpoint_limiter.get_limiter_cust("users_me")


@router.get("/users/me/info",
            tags=["Security"],
            summary="Get information about the user authenticated",
            dependencies=[Depends(RateLimiter(interval_seconds=limiter.seconds,
                                              max_requests=limiter.max_request))],
            response_model=UserOut)
async def read_current_user(request: Request,
                            current_user: User = Depends(get_current_active_user)):
    return current_user


@router.put("/users/me/update/pwd",
            tags=["Security"],
            summary="Update user password ",
            dependencies=[Depends(RateLimiter(interval_seconds=limiter.seconds,
                                              max_requests=limiter.max_request))], )
def update_current_user(user: UserUPDPassword,
                        current_user: User = Depends(get_current_active_user),
                        db: Session = Depends(get_db)):
    return update_user(user_id=current_user.id,
                       full_name="",
                       password=user.password,
                       db=db)


if enable_users:
    # Routes for user management
    @router.post("/users/",
                 tags=["Security"],
                 summary="Create new user",
                 dependencies=[Depends(RateLimiter(interval_seconds=limiter.seconds,
                                                   max_requests=limiter.max_request))],
                 response_model=UserOut)
    def create_new_user(user: UserCreate,
                        current_user: User = Depends(get_current_active_user),
                        db: Session = Depends(get_db)):
        if current_user.is_admin:
            return create_user(user=user,
                               db=db)
        else:
            raise HTTPException(status_code=403,
                                detail="You are not authorized.Permission denied")


    @router.get("/users/",
                tags=["Security"],
                summary="Get all user registered",
                dependencies=[Depends(RateLimiter(interval_seconds=limiter.seconds,
                                                  max_requests=limiter.max_request))],
                response_model=List[UserOut])
    def read_users(db: Session = Depends(get_db)):
        return get_all_users(db)


    @router.get("/users/{user_id}",
                tags=["Security"],
                summary="Get user data",
                dependencies=[Depends(RateLimiter(interval_seconds=limiter.seconds,
                                                  max_requests=limiter.max_request))],
                response_model=UserOut)
    def read_user(user_id: uuid.UUID, db: Session = Depends(get_db)):
        user = get_user(user_id=user_id,
                        db=db)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user


    @router.delete("/users/{user_id}",
                   tags=["Security"],
                   summary="Delete user",
                   dependencies=[Depends(RateLimiter(interval_seconds=limiter.seconds,
                                                     max_requests=limiter.max_request))], )
    def delete_existing_user(user_id: uuid.UUID,
                             current_user: User = Depends(get_current_active_user),
                             db: Session = Depends(get_db)):
        if current_user.is_admin:
            return delete_user(user_id=user_id,
                               db=db)
        else:
            raise HTTPException(status_code=403,
                                detail="You are not authorized.Permission denied")

    @router.put("/users/{user_id}/disable",
                tags=["Security"],
                summary="Disable user",
                dependencies=[Depends(RateLimiter(interval_seconds=limiter.seconds,
                                                  max_requests=limiter.max_request))], )
    def disable_existing_user(user_id: uuid.UUID,
                              current_user: User = Depends(get_current_active_user),
                              db: Session = Depends(get_db)):
        if current_user.is_admin:
            return disable_user(user_id=user_id,
                                db=db)
        else:
            raise HTTPException(status_code=403,
                                detail="You are not authorized.Permission denied")



import uuid

from fastapi import Depends, HTTPException, Request
from jose import jwt, JWTError
from requests import Session
from starlette import status
from starlette.responses import Response
from typing import Optional
from configs.config_boot import config_app

from datetime import timedelta, datetime

from database.db_connection import SessionLocal, get_db
from models.db.refresh_token import RefreshToken

from utils.logger_boot import logger

from security.authentication.dependencies import oauth2_scheme
from security.authentication.built_in_authentication.users import get_user_by_name
from models.user_session import UserSession
from security.schemas.token import TokenSession

token_access_expire = config_app.security.token_expiration
token_refresh_expires_days = config_app.security.refresh_token_expiration

secret_access_key = config_app.security.token_key
secret_refresh_key = config_app.security.refresh_token_key

algorithm = config_app.security.algorithm


#
# access token
#
def __create_access_token(data: dict, expires_delta: timedelta = None):
    logger.debug(f"create_access_token")
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    # LS 2024.12.12 check token key
    # encoded_jwt = jwt.encode(to_encode, secret_access_key, algorithm=algorithm)
    access_key = config_app.security.token_key
    encoded_jwt = jwt.encode(to_encode, access_key, algorithm=algorithm)
    return encoded_jwt


def __delete_user_token(user_id: uuid.UUID,
                        db: SessionLocal):
    logger.debug(f"__delete_user_token")

    db_token = db.query(RefreshToken).filter(RefreshToken.user_id == user_id).first()
    if db_token:
        db.delete(db_token)
        db.commit()
        return True
    return False


def __add_user_token(token: str,
                     user_id: uuid.UUID,
                     db: SessionLocal):
    logger.debug(f"_add_user_token")
    new_token = RefreshToken(user_id=user_id,
                             token=token)
    db.add(new_token)
    db.commit()
    return True


#
# refresh token
#

def __add_refresh_token(refresh_token: str,
                        user_id: uuid.UUID,
                        db: SessionLocal):
    logger.debug(f"add_refresh_token")
    res = __delete_user_token(user_id=user_id,
                              db=db)
    logger.debug(f"add_refresh_token.delete old token: {res}")

    __add_user_token(token=refresh_token,
                     user_id=user_id,
                     db=db)


def __create_refresh_token(data: dict, expires_delta: timedelta = None):
    logger.debug(f"create_refresh_token")
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)

    to_encode.update({"exp": expire})
    # LS 2024.12.12 check refresh key token
    # encoded_jwt = jwt.encode(to_encode, secret_refresh_key, algorithm=algorithm)
    refresh_key = config_app.security.refresh_token_key
    encoded_jwt = jwt.encode(to_encode, refresh_key, algorithm=algorithm)
    return encoded_jwt


def __get_refresh_token_by_user(token: str,
                                user_id: uuid.UUID,
                                db: SessionLocal) -> Optional[RefreshToken]:
    logger.debug(f"__get_refresh_token_by_user")
    data = db.query(RefreshToken).filter(RefreshToken.token == token,
                                         RefreshToken.user_id == user_id).first()
    if data:
        return data
    return None


#
# access token
#
def create_token(username, userid, auth_type='BUILT-IN', db: Session = None, only_access=True):
    logger.debug(f"create_token username:{username}")
    access_token_expires = timedelta(minutes=token_access_expire)

    data = {
        "sub": str(userid),
        "username": username,
        "auth_type": auth_type,
    }
    access_token = __create_access_token(
        data=data, expires_delta=access_token_expires
    )

    if not only_access:
        refresh_token_expires = timedelta(days=token_refresh_expires_days)
        # UNCOMMENT to test
        # refresh_token_expires = timedelta(minutes=3)
        # data = {
        #     "sub": str(userid),
        #     "username": username,
        #     "auth_type": auth_type,
        # }
        refresh_token = __create_refresh_token(
            data=data, expires_delta=refresh_token_expires
        )
        logger.debug(f"user name: {username} id: {userid} refresh expires:{refresh_token_expires}")
        # Update the user's refresh token in the database
        __add_refresh_token(refresh_token=refresh_token,
                            user_id=userid,
                            db=db)

        return {"access_token": access_token,
                "token_type": "bearer",
                "refresh_token": refresh_token,
                "expires_in": str(access_token_expires.seconds)}
    else:
        return {"access_token": access_token,
                "token_type": "bearer",
                "expires_in": str(access_token_expires.seconds)}


#
# uncomment to enable session with cookies (no 2/3)
#
# async def get_user_entity_from_token(token = None , request: Request = None) -> UserSession:
#     token = token or request.cookies.get("auth_token")  # ⬅️ Read from cookie
async def get_user_entity_from_token(token: str = Depends(oauth2_scheme)) -> UserSession:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    payload = None
    try:
        # LS 2024.12.12 reload from env
        # payload = jwt.decode(token, secret_access_key, algorithms=[algorithm])
        access_key = config_app.security.token_key
        payload = jwt.decode(token, access_key, algorithms=[algorithm])

        sub: str = payload.get('sub')
        username: str = payload.get('username')
        auth_type: str = payload.get('auth_type')

        if username is None:
            raise credentials_exception
        token_data = TokenSession(sub=sub, username=username, auth_type=auth_type)
    except JWTError:
        logger.error(f"Invalid token: {token} payload: {str(payload if payload is not None else '<n.a.>')}")
        raise credentials_exception

    # LDAP USER
    if payload.get('auth_type') == 'LDAP':
        user = UserSession(username=payload.get('username'),
                           is_ldap=True)
        return user

    # NATS USER
    if payload.get('is_nats'):
        user = UserSession(username="nats",
                           is_nats=True)
        # user.cp_mapping_user = request.headers.get('cp_user')
        return user
    db = next(get_db())
    try:
        user = get_user_by_name(db=db,
                                username=token_data.username)
        user_entity = UserSession(uid=user.id,
                                  username=user.username)
    finally:
        db.close()

    if user is None:
        raise credentials_exception
    return user_entity


#
# refresh token
#
def check_refresh_token_in_db(refresh_token: str,
                              user_id: uuid.UUID,
                              db: SessionLocal):
    logger.debug(f"check_refresh_token_in_db {user_id}")
    ret = False
    if refresh_token is not None:
        data = __get_refresh_token_by_user(token=refresh_token,
                                           user_id=user_id,
                                           db=db)
        if data is not None:
            ret = True
        else:
            logger.warning(f"check auth refresh token: "
                           f"user has another token in db {refresh_token[:4]}")

    if not ret:
        logger.warning(f"check auth refresh token: not in db")
        return Response("Could not validate refresh token",
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        headers={'WWW-Authenticate': 'Bearer'})

    logger.debug(f"check auth refresh token: accepted")
    return ret


def verify_refresh_token(token: str):
    logger.debug(f"verify_refresh_token")
    try:
        username = ''
        # LS 2024.12.12 check refresh token
        # payload = jwt.decode(token, secret_refresh_key, algorithms=[algorithm])
        refresh_key = config_app.get_security_refresh_token_key()
        payload = jwt.decode(token, refresh_key, algorithms=[algorithm])

        if payload is not None:
            logger.debug(f"verify_refresh_token: {payload}")
            username: str = payload.get("username")
            if username is None:
                return Response("Could not validate request-user",
                                status_code=status.HTTP_401_UNAUTHORIZED,
                                headers={'WWW-Authenticate': 'Bearer'})

        return username
    except JWTError as jwe:
        logger.warning(f"verify_refresh_token {jwe}")
        return Response("Could not validate request",
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        headers={'WWW-Authenticate': 'Bearer'})

# async def get_user_from_token(token: str = Depends(oauth2_scheme)) -> UserOut:
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail='Could not validate credentials',
#         headers={'WWW-Authenticate': 'Bearer'},
#     )
#     try:
#         logger.info(f"get_current_user_token.secret key=>{secret_access_key}")
#         # LS 2024.12.12 reload key
#         # payload = jwt.decode(token, secret_access_key, algorithms=[algorithm])
#         access_key = config_app.get_security_access_token_key()
#
#         payload = jwt.decode(token, access_key, algorithms=[algorithm])
#         username: str = payload.get('sub')
#         if username is None:
#             raise credentials_exception
#         token_data = TokenData(username=username)
#     except JWTError:
#         raise credentials_exception
#
#     # LDAP USER
#     if payload.get('auth_type') == 'LDAP':
#         user = User()
#         user.username = payload.get('username')
#         user.is_ldap = True
#         return user
#
#     user = get_user_by_name(db=SessionLocal(),
#                             username=token_data.username)
#     if user is None:
#         raise credentials_exception
#     return user

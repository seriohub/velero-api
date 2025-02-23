import re
import uuid
from fastapi import HTTPException
# from security.schemas.schemas import UserOut, UserCreate
from configs.config_boot import config_app  # , get_configmap_parameter, get_secret_parameter

from typing import Optional
from security.authentication.dependencies import pwd_context
from database.db_connection import SessionLocal
# from security.authentication.built_in_authentication.database import Configs
from models.db.user import User

from utils.logger_boot import logger



disable_password_rate = config_app.get_security_disable_pwd_rate()
secret_access_key = config_app.get_security_access_token_key()
algorithm = config_app.get_security_algorithm()


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def rate_password_strength(password):
    if disable_password_rate:
        return 'NoCheck'
    else:
        # Define a dictionary of regex patterns and their corresponding complexity scores
        complexity_patterns = {
            r".{8,}": 1,  # Minimum length of 8 characters
            r"(?=.*\d)": 1,  # At least one digit
            r"(?=.*[a-z])": 1,  # At least one lowercase letter
            r"(?=.*[A-Z])": 1,  # At least one uppercase letter
            r"(?=.*[!@#$%^&*()\-_=+{};:,<.>])": 1  # At least one special character
        }

        complexity_score = 0

        # Check each complexity pattern against the password
        for pattern, score in complexity_patterns.items():
            if re.search(pattern, password):
                complexity_score += score

        # Rate the password based on the complexity score
        if complexity_score <= 1:
            return 'Weak'
        elif complexity_score <= 3:
            return 'Medium'
        else:
            return 'Strong'


def control_data(user_id: uuid.UUID = None,
                 username: str = '',
                 password: str = '',
                 db: SessionLocal = None):
    # password rate
    if rate_password_strength(password) == 'Weak':
        raise HTTPException(status_code=403, detail='The password is weak')
    if len(username) > 0:
        if user_id is not None:
            # unique username
            user = db.query(User).filter(User.username == username).first()
        else:
            user = db.query(User).filter(User.id != user_id, User.username == username).first()

        if user:
            raise HTTPException(status_code=403, detail='The username is not unique')

    if user_id is not None:
        # hashed_password = hash_password(password)
        # print(f"user_id={user_id}-pwd={password}-hash={hashed_password}")
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            res = verify_password(plain_password=password,
                                  hashed_password=user.password)
            if res:
                raise HTTPException(status_code=403, detail={
                    'error': {'title': 'Forbidden', 'description': 'The old password is equal to the new password'}})
        else:
            raise HTTPException(status_code=403, detail='The user is deleted')
    return True


# def create_user(user: UserCreate, db: SessionLocal) -> UserOut:
#     if control_data(user_id=None,
#                     username=user.username,
#                     password=user.password,
#                     db=db):
#         hashed_password = hash_password(user.password)
#         db_user = User(username=user.username,
#                        full_name=user.full_name,
#                        password=hashed_password,
#                        is_admin=user.is_admin)
#         db.add(db_user)
#         db.commit()
#         db.refresh(db_user)
#         return db_user


# def get_user(user_id: uuid.UUID, db: SessionLocal) -> Optional[UserOut]:
#     user = db.query(User).filter(User.id == user_id, User.is_disabled == False).first()  # Filters out disabled users
#     if user:
#         return user
#     return None


# def get_user_by_name(username: str, db: SessionLocal = Depends(get_db)) -> Optional[UserOut]:
def get_user_by_name(username: str, db: SessionLocal) -> Optional[User]:
    return db.query(User).filter(User.username == username, User.is_disabled == False).first()


# def get_all_users(db: SessionLocal) -> List[UserOut]:
#     return db.query(User).all()
#
#
# def delete_user(user_id: uuid.UUID, db: SessionLocal):
#     db_user = db.query(User).filter(User.id == user_id).first()
#     if db_user:
#         if db_user.is_default:
#             raise HTTPException(status_code=403, detail='Cannot delete the default user')
#         db.delete(db_user)
#         db.commit()
#         return {"message": 'User deleted successfully'}
#     else:
#         raise HTTPException(status_code=404, detail='User not found')


def create_default_user(db: SessionLocal):
    logger.info("create_default_user.check")
    default_username = config_app.get_default_admin_username()
    default_user = db.query(User).filter(User.username == default_username).first()
    if default_user is None:
        logger.info("create_default_user.forced")
        default_password = config_app.get_default_admin_password()
        hashed_default_password = hash_password(default_password)
        new_default_user = User(username=default_username,
                                full_name='administrator',
                                password=hashed_default_password,
                                is_default=True,
                                is_admin=True,
                                is_disabled=False)
        db.add(new_default_user)
        db.commit()


# def disable_user(user_id: uuid.UUID, db: SessionLocal):
#     db_user = db.query(User).filter(User.id == user_id).first()
#     if db_user:
#         if db_user.is_default:
#             raise HTTPException(status_code=403, detail='Cannot disable the default user')
#         db_user.is_disabled = True
#         db.commit()
#         return {'message': 'User disabled successfully'}
#     else:
#         raise HTTPException(status_code=404, detail='User not found')


def update_user(user_id: uuid.UUID, full_name: str, password: str, db: SessionLocal):
    if control_data(user_id=user_id,
                    username='',
                    password=password,
                    db=db):
        db_user = db.query(User).filter(User.id == user_id).first()
        if db_user:
            if len(full_name) > 0:
                db_user.full_name = full_name
            db_user.password = hash_password(password)

            db.commit()
            # data = {'title': 'Update Password', 'description': 'User updates successfully!'}
            return True
        else:
            # raise HTTPException(status_code=404, detail='User not found')
            return False


def authenticate_user(db, username: str, password: str):
    user = get_user_by_name(username, db)
    if not user:
        logger.warning(f"Login denied for :{username}")
        return False
    res = verify_password(plain_password=password,
                          hashed_password=user.password)
    if not res:
        logger.warning(f"Access failed for :{username}")
        return False
    logger.info(f"Login in :{username}")
    return user


# LS 2024.03.18 moved in tokens.py script
# def create_access_token(data: dict, expires_delta: timedelta | None = None):
#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.utcnow() + expires_delta
#     else:
#         expire = datetime.utcnow() + timedelta(minutes=2)
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, secret_access_key, algorithm=algorithm)
#
#     return encoded_jwt
#


# def add_config_prop(db, pro):
#     tmp = db.query(Configs).filter(
#         Configs.module == 'watchdog', Configs.key == pro).first()
#     if tmp is None:
#         tmp = Configs(module='watchdog',
#                       key=pro,
#                       value=get_configmap_parameter(config_app.get_k8s_velero_ui_namespace(),
#                                                     'velero-watchdog-config',
#                                                     pro))
#         db.add(tmp)
#         db.commit()
#
#
# def add_service(db, key, value):
#     tmp = db.query(Configs).filter(
#         Configs.module == 'watchdog', Configs.value.startswith(value.split("/")[0])).first()
#     if tmp is None:
#         tmp = Configs(module='watchdog',
#                       key=key,
#                       value=value)
#         db.add(tmp)
#         db.commit()
#
#
# def create_default_config(db: SessionLocal):
#     logger.info("create_default_config")
#
#     # db
#     add_config_prop(db, 'BACKUP_ENABLED')
#     add_config_prop(db, 'SCHEDULE_ENABLED')
#     add_config_prop(db, 'NOTIFICATION_SKIP_COMPLETED')
#     add_config_prop(db, 'NOTIFICATION_SKIP_DELETING')
#     add_config_prop(db, 'NOTIFICATION_SKIP_INPROGRESS')
#     add_config_prop(db, 'NOTIFICATION_SKIP_REMOVED')
#     add_config_prop(db, 'PROCESS_CYCLE_SEC')
#     add_config_prop(db, 'EXPIRES_DAYS_WARNING')
#     add_config_prop(db, 'REPORT_BACKUP_ITEM_PREFIX')
#     add_config_prop(db, 'REPORT_SCHEDULE_ITEM_PREFIX')
#
#
# def create_default_secret_services(db: SessionLocal):
#     logger.info("create_default_config")
#
#     services = get_secret_parameter(config_app.get_k8s_velero_ui_namespace(),
#                                     'velero-watchdog-config',
#                                     'APPRISE').strip().split(";")
#
#     for service in services:
#         add_service(db, 'services', service.strip())

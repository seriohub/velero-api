from starlette import status
from starlette.responses import Response

from configs.config_boot import config_app
# from security.schemas.response.authentication import AuthenticationResponse
from security.authentication.tokens import verify_refresh_token, check_refresh_token_in_db, create_token
from security.authentication.built_in_authentication.users import authenticate_user, get_user_by_name
from database.db_connection import get_db

from security.authentication.ldap.ldap_manager import LdapManager

from utils.logger_boot import logger

ldapManager = None
if config_app.app.auth_type == 'LDAP':
    ldapManager = LdapManager()


# token_access_expire = config_app.get_security_token_expiration()
# token_refresh_expires_days = config_app.get_security_token_refresh_expiration()
# response_data = AuthenticationResponse()


def login_service(username, password):
    if config_app.app.auth_type == 'BUILT-IN':
        db = next(get_db())
        try:
            logger.debug(f"User:{username}-Password:{password[:2]}**")
            if len(username) > 1 and len(password) > 1:
                user = authenticate_user(db=db,
                                         username=username,
                                         password=password)
                if user:
                    return create_token(username=user.username,
                                        userid=user.id,
                                        db=db,
                                        only_access=False)
                else:
                    return Response("Incorrect username or password'",
                                    status_code=status.HTTP_401_UNAUTHORIZED,
                                    headers={'WWW-Authenticate': 'Bearer'})
        finally:
            db.close()
    elif config_app.app.auth_type == 'LDAP':
        logger.info("Try LDAP AUTHENTICATION")
        user = ldapManager.ldap_authenticate(username, password)
        if user:
            return create_token(username=user['username'],
                                userid=user['id'],
                                auth_type='LDAP',
                                only_access=True)
        else:
            return Response("Incorrect username or password'",
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            headers={'WWW-Authenticate': 'Bearer'})

    else:
        return Response("Username o password parameters missed",
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        headers={'WWW-Authenticate': 'Bearer'})

# def refresh_token_service(refresh_token):
#     if config_app.get_auth_type() == 'BUILT-IN':
#         db = next(get_db())
#         try:
#             logger.debug(f"refresh token")
#             username = verify_refresh_token(refresh_token)
#             logger.debug(f"refresh token- username : {username}")
#             user = None
#
#             if username is not None:
#                 if not response_data.is_response(username):
#                     user = get_user_by_name(username, db)
#                 else:
#                     logger.debug(f"refresh token- discard")
#                     return username
#
#             if username is not None and user is not None:
#                 response = check_refresh_token_in_db(refresh_token=refresh_token,
#                                                      user_id=user.id,
#                                                      db=db)
#                 if not response_data.is_response(response):
#                     return create_token(username=user.username,
#                                         userid=user.id,
#                                         db=db)
#                 else:
#                     return response
#             else:
#                 return Response("User not valid",
#                                 status_code=status.HTTP_401_UNAUTHORIZED,
#                                 headers={'WWW-Authenticate': 'Bearer'})
#         finally:
#             db.close()

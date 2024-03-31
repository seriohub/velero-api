from datetime import timedelta

from requests import Session
from starlette import status
from starlette.responses import Response

from core.config import ConfigHelper
from security.helpers.reponse import ResponseData
from security.service.helpers.tokens import create_access_token, create_refresh_token, add_refresh_token, \
    verify_refresh_token, \
    check_refresh_token_in_db
from security.service.helpers.users import authenticate_user, get_user_by_name

from helpers.printer import PrintHelper

config = ConfigHelper()


class AuthenticationService:

    def __init__(self):
        self.token_access_expire = config.get_security_token_expiration()
        self.token_refresh_expires_days = config.get_security_token_refresh_expiration()

        self.print_ls = PrintHelper('[service.authentication]',
                                    level=config.get_internal_log_level())

        self.response_data = ResponseData()

    def login(self, username, password, db: Session):
        self.print_ls.debug(f"User:{username}-Password:{password[:2]}**")
        if len(username) > 1 and len(password) > 1:
            user = authenticate_user(db=db,
                                     username=username,
                                     password=password)
            if not user:
                return Response("Incorrect username or password'",
                                status_code=status.HTTP_401_UNAUTHORIZED,
                                headers={'WWW-Authenticate': 'Bearer'})

            access_token_expires = timedelta(minutes=self.token_access_expire)
            access_token = create_access_token(
                data={'sub': user.username}, expires_delta=access_token_expires
            )
            # LS 2024.03.18 comment and add refresh token mechanism (more robust)
            # return {'access_token': access_token, 'token_type': 'bearer'}

            refresh_token_expires = timedelta(days=self.token_refresh_expires_days)
            # UNCOMMENT to test
            # refresh_token_expires = timedelta(minutes=3)

            refresh_token = create_refresh_token(
                data={"sub": user.username}, expires_delta=refresh_token_expires
            )
            self.print_ls.debug(f"user name: {user.username} id: {user.id}")
            # Update the user's refresh token in the database
            add_refresh_token(refresh_token=refresh_token,
                              user_id=user.id,
                              db=db)

            return {"access_token": access_token,
                    "token_type": "bearer",
                    "refresh_token": refresh_token}
        else:
            return Response("Username o password parameters missed",
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            headers={'WWW-Authenticate': 'Bearer'})

    def refresh_token(self, refresh_token, db: Session):
        self.print_ls.debug(f"refresh token")
        username = verify_refresh_token(refresh_token)
        self.print_ls.debug(f"refresh token- username : {username}")
        user = None

        if username is not None:
            if not self.response_data.is_response(username):
                user = get_user_by_name(username, db)
            else:
                self.print_ls.debug(f"refresh token- discard")
                return username

        if username is not None and user is not None:
            response = check_refresh_token_in_db(refresh_token=refresh_token,
                                                 user_id=user.id,
                                                 db=db)
            if not self.response_data.is_response(response):
                access_token_expires = timedelta(minutes=self.token_access_expire)
                access_token = create_access_token(
                    data={'sub': username}, expires_delta=access_token_expires
                )

                return {"access_token": access_token, "token_type": "bearer"}
            else:
                return response
        else:
            return Response("User not valid",
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            headers={'WWW-Authenticate': 'Bearer'})

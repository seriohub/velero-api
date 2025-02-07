from requests import Session

from security.service.autenthication import AuthenticationService
from utils.handle_exceptions import handle_exceptions_controller

authenticationService = AuthenticationService()


class Authentication:

    @handle_exceptions_controller
    async def login(self, username, password, db: Session):
        # print(f"controller un:{username} pwd: {password}")
        # payload = authenticationService.login(username, password, db)
        # return payload
        return authenticationService.login(username, password, db)

    @handle_exceptions_controller
    async def refresh_login(self, refresh_token, db: Session):
        # print(f"refresh_login refresh_token :{refresh_token}")
        return authenticationService.refresh_token(refresh_token, db)

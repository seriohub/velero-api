from security.service.authentication import AuthenticationService
from utils.handle_exceptions import handle_exceptions_controller

authenticationService = AuthenticationService()


class Authentication:

    @handle_exceptions_controller
    async def login(self, username, password):
        return authenticationService.login(username, password)

    @handle_exceptions_controller
    async def refresh_login(self, refresh_token):
        return authenticationService.refresh_token(refresh_token)

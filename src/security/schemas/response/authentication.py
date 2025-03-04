from starlette.responses import HTMLResponse, JSONResponse, RedirectResponse, Response

from configs.config_boot import config_app

from utils.logger_boot import logger




class AuthenticationResponse:

    def is_response(self, response):
        logger.debug(f"is_response")
        return isinstance(response, (Response,
                                     HTMLResponse,
                                     JSONResponse,
                                     RedirectResponse))

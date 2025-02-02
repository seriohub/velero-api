from starlette.responses import HTMLResponse, JSONResponse, RedirectResponse, Response

from core.config import ConfigHelper
from helpers.logger import ColoredLogger, LEVEL_MAPPING
import logging

config_app = ConfigHelper()
logger = ColoredLogger.get_logger(__name__, level=LEVEL_MAPPING.get(config_app.get_internal_log_level(), logging.INFO))


class ResponseData:

    def is_response(self, response):
        logger.debug(f"is_response")
        return isinstance(response, (Response,
                                     HTMLResponse,
                                     JSONResponse,
                                     RedirectResponse))

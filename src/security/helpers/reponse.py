from starlette.responses import HTMLResponse, JSONResponse, RedirectResponse, Response

from app_data import config_app
from helpers.printer import PrintHelper


class ResponseData:

    def __init__(self):
        self.print_ls = PrintHelper('[helper.response]',
                                    level=config_app.get_internal_log_level())

    def is_response(self, response):
        self.print_ls.debug(f"is_response")
        return isinstance(response, (Response,
                                     HTMLResponse,
                                     JSONResponse,
                                     RedirectResponse))

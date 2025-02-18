from fastapi import Request
import sys
from core.config import ConfigHelper

from helpers.logger import ColoredLogger, LEVEL_MAPPING
import logging

config_app = ConfigHelper()
logger = ColoredLogger.get_logger(__name__, level=LEVEL_MAPPING.get(config_app.get_internal_log_level(), logging.INFO))


class IpClient:

    def extract_ip_from_request(self, request: Request):
        try:
            logger.debug(f"extract_ip_from_request")
            if not request.client or not request.client.host:
                logger.debug(f'client remote not found return None')
                return "127.0.0.1"

            if not request.headers:
                logger.debug(f'client remote header not found return None')
                return "127.0.0.1"

            client_ip_aux = request.headers.getlist("x-forwarded-for")

            if client_ip_aux is None or len(client_ip_aux) == 0:
                logger.debug('client remote header not no xREAL in header')
                return "127.0.0.1"

            return client_ip_aux[0]
        except Exception as ex:  # catch *all* exceptions
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.warning(f'extract_ip_from_request.{exc_tb.tb_lineno}  {str(ex)}')
            return None

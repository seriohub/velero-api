from fastapi import Request
import sys
from configs.config_boot import config_app

from utils.logger_boot import logger


def extract_ip_from_request(request: Request):
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

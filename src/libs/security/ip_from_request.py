# import secrets
from fastapi import Request
from helpers.printer_helper import PrintHelper
import sys


class IpClient:
    def __init__(self,
                 debug: bool,
                 info: bool):

        self.info = info
        self.debug = debug
        self.print_ls = PrintHelper('[IpClient]')

    def extract_ip_from_request(self, request: Request):
        try:
            self.print_ls.info_if(self.info, f"extract_ip_from_request")
            if not request.client or not request.client.host:
                self.print_ls.debug_if(self.debug, f'INFO: client remote not found return None')
                return "127.0.0.1"

            if not request.headers:
                self.print_ls.debug_if(self.debug,
                                       f'INFO: client remote header not found return None')
                return "127.0.0.1"

            client_ip_aux = request.headers.getlist("x-forwarded-for")

            if client_ip_aux is None or len(client_ip_aux) == 0:
                self.print_ls.debug_if(self.debug,
                                       f'INFO: client remote header not no xREAL in header')
                return "127.0.0.1"

            return client_ip_aux[0]
        except Exception as ex:  # catch *all* exceptions
            exc_type, exc_obj, exc_tb = sys.exc_info()
            self.print_ls.wrn(f'extract_ip_from_request.{exc_tb.tb_lineno}  {str(ex)}')
            return None

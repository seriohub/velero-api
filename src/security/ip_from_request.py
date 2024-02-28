# import secrets
from fastapi import Request
from helpers.printer import PrintHelper
import sys


class IpClient:
    def __init__(self, level):
        self.print_ls = PrintHelper('[authentication.ip_client]',
                                    level=level)

    def extract_ip_from_request(self, request: Request):
        try:
            self.print_ls.trace(f"extract_ip_from_request")
            if not request.client or not request.client.host:
                self.print_ls.trace(f'client remote not found return None')
                return "127.0.0.1"

            if not request.headers:
                self.print_ls.trace(f'client remote header not found return None')
                return "127.0.0.1"

            client_ip_aux = request.headers.getlist("x-forwarded-for")

            if client_ip_aux is None or len(client_ip_aux) == 0:
                self.print_ls.trace('client remote header not no xREAL in header')
                return "127.0.0.1"

            return client_ip_aux[0]
        except Exception as ex:  # catch *all* exceptions
            exc_type, exc_obj, exc_tb = sys.exc_info()
            self.print_ls.wrn(f'extract_ip_from_request.{exc_tb.tb_lineno}  {str(ex)}')
            return None

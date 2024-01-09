from datetime import datetime, timedelta
from fastapi import HTTPException, Request
from helpers.printer_helper import PrintHelper
from libs.config import ConfigEnv, LimiterRequestConfig
from libs.security.ip_from_request import IpClient


class LimiterRequests:
    def __init__(self, debug, printer, tags, default_key=None):
        self.print_ls = printer
        self.debug_on = debug
        self.requests = {}
        self.tags = tags
        self.default_key = default_key
        config = ConfigEnv()
        self.api_limiter = config.get_api_limiter(tags)

    def get_limiter_cust(self, key):
        complete_key = f"CUS_{self.tags}_{key}"
        limiter = self.get_limiter(complete_key)

        self.print_ls.info(f" limiter tags:{self.tags} key:/{key.replace('_', '/')} "
                           f"max request: {limiter.max_request} interval: {limiter.seconds} seconds")
        return limiter

    def get_limiter(self, key):
        if (self.api_limiter is not None and
                len(self.api_limiter) > 0):
            if key in self.api_limiter:
                limiter = LimiterRequestConfig(seconds=self.api_limiter[key].seconds,
                                               request=self.api_limiter[key].max_request)
            else:
                key = 'L1'
                if self.default_key is not None:
                    if self.default_key in self.api_limiter:
                        key = self.default_key

                limiter = LimiterRequestConfig(seconds=self.api_limiter[key].seconds,
                                               request=self.api_limiter[key].max_request)
        else:
            limiter = LimiterRequestConfig(seconds=60,
                                           request=100)

        return limiter


class RateLimiter:
    def __init__(self,
                 debug: bool = False,
                 info: bool = False,
                 interval_seconds: int = 60,
                 max_requests: int = 10
                 ):
        self.rate_limits = {}
        self.print_ls = PrintHelper('rateLimiter')
        self.info = info
        self.debug = debug
        self.ip_client = IpClient(debug, info)

        self.interval_seconds = interval_seconds
        self.max_requests = max_requests

    async def __call__(self, request: Request):

        self.print_ls.info_if(self.info,
                              f"limit {self.max_requests}/{self.interval_seconds}secs")

        client_ip = self._get_client_ip(request)
        self.print_ls.debug_if(self.debug,
                               f"limit client ip {client_ip}")

        current_time = datetime.now()

        try:
            if client_ip not in self.rate_limits:
                self.rate_limits[client_ip] = [(current_time, 1)]
            else:
                self._clean_expired_time_slots(client_ip, current_time, self.interval_seconds)

                total_requests = self._get_total_requests(client_ip)
                if total_requests >= self.max_requests:
                    self.print_ls.debug_if(self.debug,
                                           f"limit client ip {client_ip} Too Many Requests")

                    raise HTTPException(status_code=429, detail="too many requests")

                self._add_time_slot(client_ip, current_time)

            return True
        except HTTPException:
            raise
        except Exception as e:
            self.print_ls.debug_if(self.debug,
                                   f"limit error {e}")
            # Handle any exceptions that may occur during request processing
            # For example, log the error or return an appropriate error response
            return {"error": str(e)}

    def _get_client_ip(self,
                       request):
        self.print_ls.info_if(self.info,
                              f"_get_client_ip")
        return self.ip_client.extract_ip_from_request(request)

    def _clean_expired_time_slots(self, client_ip,
                                  current_time,
                                  interval_seconds):
        self.print_ls.info_if(self.info,
                              f"_clean_expired_time_slots")
        time_slots = self.rate_limits[client_ip]
        self.rate_limits[client_ip] = \
            [slot for slot in time_slots if current_time - slot[0] <= timedelta(seconds=interval_seconds)]

    def _get_total_requests(self,
                            client_ip):
        self.print_ls.info_if(self.info,
                              f"_get_total_requests")
        time_slots = self.rate_limits[client_ip]
        return sum([slot[1] for slot in time_slots])

    def _add_time_slot(self, client_ip, current_time):
        self.print_ls.info_if(self.info,
                              f"_add_time_slot")
        if client_ip in self.rate_limits:
            self.rate_limits[client_ip].append((current_time, 1))
        else:
            self.rate_limits[client_ip] = [(current_time, 1)]

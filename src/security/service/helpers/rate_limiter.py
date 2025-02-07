from datetime import datetime, timedelta
from fastapi import HTTPException, Request

from core.config import ConfigHelper, LimiterRequestConfig
from security.service.helpers.ip_from_request import IpClient

from helpers.logger import ColoredLogger, LEVEL_MAPPING
import logging

config_app = ConfigHelper()
logger = ColoredLogger.get_logger(__name__, level=LEVEL_MAPPING.get(config_app.get_internal_log_level(), logging.INFO))


class LimiterRequests:
    def __init__(self, tags, default_key=None):
        self.requests = {}
        self.tags = tags
        self.default_key = default_key
        self.api_limiter = config_app.get_api_limiter(tags)

    def get_limiter_cust(self, key):
        bCustom_tags = False
        complete_key = f"CUS_{self.tags}_{key}"
        if (self.api_limiter is not None and
                len(self.api_limiter) > 0):
            if complete_key in self.api_limiter:
                bCustom_tags = True

        if not bCustom_tags:
            complete_key = f"CUS_{self.tags}_xxx"

        limiter = self.get_limiter(complete_key)

        logger.debug(f"limiter tags:{self.tags} key:/{key.replace('_', '/')}, "
                     f"max request: {limiter.max_request}, interval: {limiter.seconds} seconds")
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
                 interval_seconds: int = 60,
                 max_requests: int = 10
                 ):
        self.rate_limits = {}

        self.ip_client = IpClient()

        self.interval_seconds = interval_seconds
        self.max_requests = max_requests

    async def __call__(self, request: Request):

        logger.debug(f"limit {self.max_requests}/{self.interval_seconds}secs")

        client_ip = self._get_client_ip(request)
        logger.debug(f"limit client ip {client_ip}")

        current_time = datetime.now()

        try:
            if client_ip not in self.rate_limits:
                self.rate_limits[client_ip] = [(current_time, 1)]
            else:
                self._clean_expired_time_slots(client_ip, current_time, self.interval_seconds)

                total_requests = self._get_total_requests(client_ip)
                if total_requests >= self.max_requests:
                    logger.warning(f"limit client ip {client_ip} Too Many Requests")

                    raise HTTPException(status_code=429, detail='too many requests')

                self._add_time_slot(client_ip, current_time)

            return True
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"limit error {e}")
            # Handle any exceptions that may occur during request processing
            # For example, log the error or return an appropriate error response
            return {"error": str(e)}

    def _get_client_ip(self,
                       request):
        logger.debug(f"_get_client_ip")
        return self.ip_client.extract_ip_from_request(request)

    def _clean_expired_time_slots(self, client_ip,
                                  current_time,
                                  interval_seconds):
        logger.debug(f"_clean_expired_time_slots")
        time_slots = self.rate_limits[client_ip]
        self.rate_limits[client_ip] = \
            [slot for slot in time_slots if current_time - slot[0] <= timedelta(seconds=interval_seconds)]

    def _get_total_requests(self,
                            client_ip):
        logger.debug(f"_get_total_requests")
        time_slots = self.rate_limits[client_ip]
        return sum([slot[1] for slot in time_slots])

    def _add_time_slot(self, client_ip, current_time):
        logger.debug(f"_add_time_slot")
        if client_ip in self.rate_limits:
            self.rate_limits[client_ip].append((current_time, 1))
        else:
            self.rate_limits[client_ip] = [(current_time, 1)]

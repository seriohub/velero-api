import os

from security.helpers.limiter_request_config import LimiterRequestConfig


class SecurityConfig:
    def __init__(self):
        self.token_key = os.getenv("SECURITY_TOKEN_KEY", "")
        self.refresh_token_key = os.getenv("SECURITY_REFRESH_TOKEN_KEY", "")
        self.token_expiration = int(os.getenv('API_TOKEN_EXPIRATION_MIN', '30'))
        self.refresh_token_expiration = int(os.getenv('API_TOKEN_REFRESH_EXPIRATION_DAYS', '7'))
        self.disable_pwd_rate = int(os.getenv('SECURITY_DISABLE_USERS_PWD_RATE', '0'))
        self.algorithm = os.getenv('SECURITY_ALGORITHM', 'HS256')
        self.database_path = os.getenv('SECURITY_PATH_DATABASE', './')
        self.limit_concurrency = int(os.getenv('LIMIT_CONCURRENCY', '50'))

    @staticmethod
    def get_api_limiter(path_to_load):
        limiter = {}

        for x in range(1, 10, 1):
            res = os.getenv(f'API_RATE_LIMITER_L{x}', None)
            if res is None or len(res) == 0:
                break
            else:
                data = res.split(':')
                if len(data) == 2:
                    if data[0].isdigit() and data[1].isdigit():
                        sec = int(data[0])
                        request = int(data[1])
                        if sec > 0 and request > 0:
                            # limiter = {f'L{x}': {'seconds': sec, 'requests': request}}
                            level = LimiterRequestConfig(level=x, seconds=sec, request=request)
                            limiter[f'L{x}'] = level

        if limiter is None:
            level = LimiterRequestConfig(level=1, seconds=60, request=20)
            limiter = {'L1': level}

        for x in range(1, 100, 1):
            res = os.getenv(f'API_RATE_LIMITER_CUSTOM_{x}', None)
            if res is None or len(res) == 0:
                break
            else:
                data = res.split(':')
                if len(data) == 4:
                    if (len(path_to_load) > 0 and data[0] in path_to_load) or len(path_to_load) == 0:
                        if data[2].isdigit() and data[3].isdigit():
                            sec = int(data[2])
                            request = int(data[3])
                            if sec > 0 and request > 0:
                                level = LimiterRequestConfig(level=x, seconds=sec, request=request)
                                limiter[f'CUS_{data[0]}_{data[1]}'] = level

        return limiter

    @staticmethod
    def get_origins():
        origins = []
        for x in range(1, 100, 1):
            res = os.getenv(f'ORIGINS_{x}', None)
            if res is None or len(res) == 0:
                break
            else:
                origins.append(res)
        return origins

import json
from dotenv.main import dotenv_values
from dotenv import load_dotenv, find_dotenv
import os
from helpers.handle_exceptions import handle_exceptions_instance_method


class LimiterRequestConfig:
    def __init__(self, level=1, seconds=60, request=10):
        self._level = level
        self._seconds = seconds
        self._request = request

    @property
    def level(self):
        """The level property."""
        return self._level

    @property
    def seconds(self):
        """The seconds' property."""
        return self._seconds

    @property
    def max_request(self):
        """The max_request property."""
        return self._request


# class syntax
class ConfigEnv:
    def __init__(self, debug=False):
        self.debug_on = debug
        load_dotenv()

    @handle_exceptions_instance_method
    def load_key(self, key, default, print_out: bool = True, mask_value: bool = False):
        value = os.getenv(key)
        if value is None or \
                len(value) == 0:
            value = default

        if print_out:
            if mask_value and len(value) > 2:
                index = int(len(value) / 2)
                partial = '*' * index
                if self.debug_on:
                    print(f"INFO      [Env] load_key.key={key} value={value[:index]}{partial}")
            else:
                if self.debug_on:
                    print(f"INFO      [Env] load_key.key={key} value={value}")
        return value

    @handle_exceptions_instance_method
    def logger_key(self):
        return self.load_key('LOG_KEY', 'k8s-wdt')

    @handle_exceptions_instance_method
    def logger_msg_format(self):
        default = '%(asctime)s :: [%(levelname)s] :: %(message)s'
        return self.load_key('LOG_FORMAT', default)

    @handle_exceptions_instance_method
    def logger_save_to_file(self):
        res = self.load_key('LOG_SAVE', 'False')
        return True if res.upper() == 'TRUE' else False

    @handle_exceptions_instance_method
    def logger_folder(self):
        return self.load_key('LOG_DEST_FOLDER',
                             './logs')

    @handle_exceptions_instance_method
    def logger_filename(self):
        return self.load_key('LOG_FILENAME',
                             'k8s.log')

    @handle_exceptions_instance_method
    def logger_max_filesize(self):
        return int(self.load_key('LOG_MAX_FILE_SIZE',
                                 4000000))

    @handle_exceptions_instance_method
    def logger_his_backups_files(self):
        return int(self.load_key('LOG_FILES_BACKUP',
                                 '5'))

    @handle_exceptions_instance_method
    def logger_level(self):
        return self.load_key('LOG_LEVEL', 10)

    @handle_exceptions_instance_method
    def unicorn_reload_update(self):
        return self.load_key('UNICORN_RELOAD', 'False').lower() == 'true'

    @handle_exceptions_instance_method
    def container_mode(self):
        return self.load_key('CONTAINER_MODE', 'False').lower() == 'true'

    @handle_exceptions_instance_method
    def k8s_in_cluster_mode(self):
        return self.load_key('K8S_IN_CLUSTER_MODE', 'False').lower() == 'true'

    @handle_exceptions_instance_method
    def internal_debug_enable(self):
        res = self.load_key('DEBUG', 'False')
        return True if res.lower() == 'true' or res.lower() == '1' else False

    @handle_exceptions_instance_method
    def get_path_db(self):
        res = self.load_key('SECURITY_PATH_DATABASE',
                            './')
        if len(res) > 1:
            # TODO: check, not working for absolute path
            if res.startswith('/'):
                res = res[1:]

            if res.endswith('/'):
                res = res[0:-1]
        else:
            res = './'
        return res

    @staticmethod
    def get_endpoint_url():
        endpoint_url = os.getenv('API_ENDPOINT_URL')
        if endpoint_url is None or \
                len(endpoint_url) == 0:
            endpoint_url = '127.0.0.1'
        return endpoint_url

    @staticmethod
    def get_endpoint_port():
        endpoint_port = os.getenv('API_ENDPOINT_PORT')
        if endpoint_port is None or \
                len(endpoint_port) == 0:
            endpoint_port = '8090'
        return endpoint_port

    @staticmethod
    def get_limit_concurrency():
        limit = os.getenv('LIMIT_CONCURRENCY')
        if limit is None or \
                len(limit) == 0:
            limit = '50'
        return limit

    @handle_exceptions_instance_method
    def get_velero_version(self):
        return self.load_key('VELERO_CLI_VERSION', 'velero-v1.11.1')

    @handle_exceptions_instance_method
    def get_velero_version_folder(self):
        return self.load_key('VELERO_CLI_PATH', '/velero-client')

    @handle_exceptions_instance_method
    def get_velero_dest_folder(self):
        return self.load_key('VELERO_CLI_DEST_PATH', '/usr/local/bin')

    @staticmethod
    def get_security_token_expiration():
        res = os.getenv('API_TOKEN_EXPIRATION_MIN',
                        '30')
        if len(res) == 0:
            res = '30'
        return int(res)

    @staticmethod
    def get_security_manage_users():
        res = os.getenv('SECURITY_USERS_ON', '0')
        if len(res) == 0:
            res = '0'
        return int(res)

    @staticmethod
    def get_security_disable_pwd_rate():
        res = os.getenv('SECURITY_DISABLE_USERS_PWD_RATE', '0')
        if len(res) == 0:
            res = '0'
        return int(res)

    @staticmethod
    def get_security_token_key():
        return os.getenv('SECURITY_TOKEN_KEY', 'not-defined-not-secure-provide-a-valid-key')

    @staticmethod
    def get_security_algorithm():
        return os.getenv('SECURITY_ALGORITHM', 'HS256')

    @staticmethod
    def get_security_user():
        users = {}
        rec = os.getenv(f'SECURITY_USR_NAME', '')
        if len(rec) > 0:
            users = json.loads(rec)
        return users

    @staticmethod
    def get_api_disable_documentation():
        res = os.getenv('API_ENABLE_DOCUMENTATION', '0')
        if len(res) == 0:
            res = '0'
        return int(res)

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
            level = LimiterRequestConfig(level=1, seconds=60, request=120)
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
    def get_env_variables():
        data = dotenv_values(find_dotenv())
        kv = {}
        for k, v in data.items():
            if k.startswith('SECURITY_TOKEN_KEY'):
                v = v[1].ljust(len(v) - 1, '*')
                # print(temp)
                # v = temp
            kv[k] = v
        return kv

    @staticmethod
    def get_build_version():
        return os.getenv('BUILD_VERSION', 'dev')

    @staticmethod
    def get_date_build():
        return os.getenv('BUILD_DATE', '-')

    @staticmethod
    def get_admin_email():
        return os.getenv('ADMIN_EMAIL', 'not set')

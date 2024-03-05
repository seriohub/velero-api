import json
import re
import os

from dotenv.main import dotenv_values
from dotenv import load_dotenv, find_dotenv


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
class ConfigHelper:
    def __init__(self, debug=False):
        self.debug_on = debug
        load_dotenv()

    @staticmethod
    def __validate_rate_limiter__(input_str):
        # Regular expression pattern to match the format "string:string:int:int"
        pattern = re.compile(r'^[^:]+:[^:]+:\d+:\d+$')

        # Check if the input string matches the pattern
        if not re.match(pattern, input_str):
            return False

        # Split the input string by colon ':'
        parts = input_str.split(':')

        # Check if the string parts are not empty
        if not all(parts[:2]):
            return False

        # Check if the integer parts are greater than 0
        try:
            int_parts = map(int, parts[2:])
            if any(i <= 0 for i in int_parts):
                return False
        except ValueError:
            return False

        return True

    @staticmethod
    def __validate_url__(url, check_protocol=True):
        protocol_part = "(?:(?:http|ftp)s?://)?" if not check_protocol else "(?:http|ftp)s?://"
        # Regular expression for URL validation
        regex = re.compile(
            rf'^{protocol_part}'  # http:// or https:// or ftp:// optionally
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or IP
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        return re.match(regex, url) is not None

    @staticmethod
    def __is_valid_secret_key__(token):
        # Check if the token consists only of hexadecimal characters
        if all(c.isdigit() or c.lower() in 'abcdef' for c in token):
            # Check if the length of the token is within the specified range
            if 10 <= len(token) <= 90:
                return True
        return False

    @staticmethod
    def __is_path_exists__(path):
        return os.path.exists(path)

    @staticmethod
    def __check_integer_sequence__(text):
        # Regular expression pattern to match the format with integers greater than 0
        pattern = re.compile(r'\b([1-9]\d*):([1-9]\d*)\b')

        # Check if the pattern is found in the text
        return bool(re.search(pattern, text))

    @staticmethod
    def __validate_env_variable__(env_var_name, var_type):
        res = True
        env_var_value = os.getenv(env_var_name)
        message = ""

        if env_var_value is None:
            message = f"****error is not set"
            return None, message

        try:
            if var_type == int:
                value = int(env_var_value)
                if value == 0:
                    res = False
                    message = f"****value (0) is not valid"
                else:
                    message = "OK"

            elif var_type == float:
                value = float(env_var_value)
                message = "OK"

            elif var_type == str:
                value = str(env_var_value)
                message = "OK"

            elif var_type == bool:
                message = 'OK' if env_var_value.lower() in ['true', '1', '0', 'false'] \
                    else '****error cast value'

            else:
                res = False
                message = "****error invalid type specified."

        except ValueError:
            res = False
            message = f"****error cast value"
        finally:
            print(f"INFO      [Env validation] key: {env_var_name.ljust(35, ' ')} "
                  f"type:{var_type.__name__.ljust(10, ' ')} "
                  f"value:{env_var_value.ljust(25, ' ')} "
                  f"validation:{message.upper()}")
            return res

    def validate_env_variables(self):
        print(f"INFO      [Env validation] Check the validity all env variables")
        block_exec = False
        all_env = {'UNICORN_RELOAD': {'type': bool, 'is_mandatory': False},
                   'CONTAINER_MODE': {'type': bool, 'is_mandatory': False},
                   'K8S_IN_CLUSTER_MODE': {'type': bool, 'is_mandatory': False},
                   'K8S_VELERO_NAMESPACE': {'type': str, 'is_mandatory': False},
                   'API_ENDPOINT_PORT': {'type': int, 'is_mandatory': True},
                   'API_ENABLE_DOCUMENTATION': {'type': int, 'is_mandatory': True},
                   'API_TOKEN_EXPIRATION_MIN': {'type': int, 'is_mandatory': True},
                   'SECURITY_DISABLE_USERS_PWD_RATE': {'type': bool, 'is_mandatory': False},
                   'LIMIT_CONCURRENCY': {'type': int, 'is_mandatory': False}}

        for key, value in all_env.items():
            res = self.__validate_env_variable__(key, value['type'])
            if not res and value['is_mandatory']:
                block_exec = True

        # init the dict for url keys
        urls = {'API_ENDPOINT_URL': {'protocol': False}}
        # origins
        for x in range(1, 100, 1):
            urls[f'ORIGINS_{x}'] = {'protocol': True}

        for key, value in urls.items():
            res = os.getenv(key, None)
            if res is None or len(res) == 0:
                break
            else:
                message = "OK" if res == '*' or self.__validate_url__(res, value['protocol']) else "error not a url"
                print(f"INFO      [Env validation] key: {key.ljust(35, ' ')} "
                      f"type:{'url'.ljust(10, ' ')} "
                      f"value:{res.ljust(25, ' ')} "
                      f"validation:{message.upper()}")
                if message != "OK":
                    block_exec = True

        key = 'SECURITY_TOKEN_KEY'
        value = os.getenv(key, None)
        message = "OK" if self.__is_valid_secret_key__(value) else "error not a valid secret key"
        print(f"INFO      [Env validation] key: {key.ljust(35, ' ')} "
              f"type:{'url'.ljust(10, ' ')} "
              f"value:{value[:25].ljust(25, ' ')} "
              f"validation:{message.upper()}")
        if message != "OK":
            block_exec = True

        key = 'DEBUG_LEVEL'
        value = os.getenv(key, None)
        key_is_ok = False
        if value is not None:
            value = value.lower()
            key_is_ok = True if value in ['critical', 'error', 'warning', 'info', 'debug', 'trace', 'notset'] else False
        message = "OK" if key_is_ok else "error not a valid debug level"
        print(f"INFO      [Env validation] key: {key.ljust(35, ' ')} "
              f"type:{'string'.ljust(10, ' ')} "
              f"value:{value[:25].ljust(25, ' ')} "
              f"validation:{message.upper()}")
        if message != "OK":
            block_exec = True

        paths = ['VELERO_CLI_PATH',
                 'VELERO_CLI_DEST_PATH',
                 'SECURITY_PATH_DATABASE',
                 'VELERO_CLI_PATH']
        for key in paths:
            res = None
            value = os.getenv(key, None)
            if value is not None:
                res = self.__is_path_exists__(value)
            else:
                value = ""
            message = "OK" if res is not None else "not valid path"
            print(f"INFO      [Env validation] key: {key.ljust(35, ' ')} "
                  f"type:{'path'.ljust(10, ' ')} "
                  f"value:{value[:25].ljust(25, ' ')} "
                  f"validation:{message.upper()}")
            if not res:
                block_exec = True

        # LS 2024.02.22 custom folder (not mandatory)
        key = 'VELERO_CLI_PATH_CUSTOM'
        value = os.getenv(key, None)
        res = None
        if value is not None:
            res = self.__is_path_exists__(value)
        else:
            value = ""
        message = "OK" if res is not None else "not valid path"
        print(f"INFO      [Env validation] key: {key.ljust(35, ' ')} "
              f"type:{'path'.ljust(10, ' ')} "
              f"value:{value[:25].ljust(25, ' ')} "
              f"validation:{message.upper()}")

        key = 'API_RATE_LIMITER_L1'
        value = os.getenv(key, None)
        message = "OK" if self.__check_integer_sequence__(value) else "error not a valid rate limiter sequence"
        print(f"INFO      [Env validation] key: {key.ljust(35, ' ')} "
              f"type:{'complex'.ljust(10, ' ')} "
              f"value:{value[:25].ljust(25, ' ')} "
              f"validation:{message.upper()}")
        if message != "OK":
            block_exec = True

        # init the dict for rate limiter rules
        rate_limiters = []
        # origins
        for x in range(1, 100, 1):
            rate_limiters.append(f'API_RATE_LIMITER_CUSTOM_{x}')

        for key in rate_limiters:
            res = os.getenv(key, None)
            if res is None or len(res) == 0:
                break
            else:
                message = "OK" if self.__validate_rate_limiter__(res) else "error not a valid rate limiter "
                print(f"INFO      [Env validation] key: {key.ljust(35, ' ')} "
                      f"type:{'complex'.ljust(10, ' ')} "
                      f"value:{res.ljust(25, ' ')} "
                      f"validation:{message.upper()}")
                if message != "OK":
                    block_exec = True

        print(f"INFO      [Env validation] Mandatory env variables set: {not block_exec}")
        if block_exec:
            print(f"INFO      [Env validation] !!!Warning:The application can not start. Try to update the keys in "
                  f"errors and restart the program.")
        return block_exec

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

    def logger_key(self):
        return self.load_key('LOG_KEY', 'k8s-wdt')

    def logger_msg_format(self):
        default = '%(asctime)s :: [%(levelname)s] :: %(message)s'
        return self.load_key('LOG_FORMAT', default)

    def logger_save_to_file(self):
        res = self.load_key('LOG_SAVE', 'False')
        return True if res.upper() == 'TRUE' else False

    def logger_folder(self):
        return self.load_key('LOG_DEST_FOLDER',
                             './logs')

    def logger_filename(self):
        return self.load_key('LOG_FILENAME',
                             'k8s.log')

    def logger_max_filesize(self):
        return int(self.load_key('LOG_MAX_FILE_SIZE',
                                 4000000))

    def logger_his_backups_files(self):
        return int(self.load_key('LOG_FILES_BACKUP',
                                 '5'))

    def logger_level(self):
        return self.load_key('LOG_LEVEL', 10)

    def uvicorn_reload_update(self):
        return self.load_key('UVICORN_RELOAD', 'False').lower() == 'true'

    def container_mode(self):
        return self.load_key('CONTAINER_MODE', 'False').lower() == 'true'

    def k8s_in_cluster_mode(self):
        return self.load_key('K8S_IN_CLUSTER_MODE', 'False').lower() == 'true'

    def get_internal_log_level(self):
        res = self.load_key('DEBUG_LEVEL', None)
        if res is not None:
            lev = res.lower()
            if lev in ['critical', 'error', 'warning', 'info', 'debug', 'trace', 'notset']:
                return lev

        return "info"

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

    def get_velero_version(self):
        return self.load_key('VELERO_CLI_VERSION', 'velero-v1.11.1')

    def get_velero_version_folder(self):
        return self.load_key('VELERO_CLI_PATH', '/velero-client')

    def get_velero_version_custom_folder(self):
        return self.load_key('VELERO_CLI_PATH_CUSTOM', None)

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
        if res == '0':
            return False
        return True

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

    def get_env_variables(self):
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

    @staticmethod
    def get_k8s_velero_namespace():
        return os.getenv('K8S_VELERO_NAMESPACE', 'velero')

    @staticmethod
    def get_k8s_velero_ui_namespace():
        return os.getenv('K8S_VELERO_UI_NAMESPACE', 'velero-ui')

    @staticmethod
    def get_developer_mode():
        res = os.getenv('DEVELOPER_MODE', 'false')
        if res.lower() == 'true':
            return True
        return False

    @staticmethod
    def developer_mode_skip_download():
        res = os.getenv('SKIP_DOWNLOAD', 'false')
        if res.lower() == 'true':
            return True
        return False

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

    @staticmethod
    def k8s_pod_name():
        return os.getenv('POD_NAME')

    @staticmethod
    def k8s_pod_namespace_in():
        return os.getenv('POD_NAMESPACE')

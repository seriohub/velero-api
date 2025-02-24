import re
import os
import secrets
from dotenv.main import dotenv_values
from dotenv import load_dotenv, find_dotenv

from configs.logger import LoggerConfig
from configs.security import SecurityConfig
from configs.kubernetes import KubernetesConfig

from configs.nats import NATSConfig
from configs.ldap import LDAPConfig
from configs.helm import HelmConfig
from configs.application import ApplicationConfig
from configs.api import APIConfig
from configs.database import DatabaseConfig
from configs.watchdog import WatchdogConfig
from configs.locations import LocationConfig


class ConfigHelper:
    def __init__(self):
        load_dotenv()
        self.logger = LoggerConfig()
        self.security = SecurityConfig()
        self.k8s = KubernetesConfig()
        self.nats = NATSConfig()
        self.ldap = LDAPConfig()
        self.helm = HelmConfig()
        self.app = ApplicationConfig()
        self.api = APIConfig()
        self.database = DatabaseConfig()
        self.watchdog = WatchdogConfig()
        self.location = LocationConfig()

    # ------------------------------------------------------------------------------------------------
    #             UTILS
    # ------------------------------------------------------------------------------------------------

    @staticmethod
    def __is_valid_secret_key__(token):
        # Check if the token consists only of hexadecimal characters
        if token is not None and len(token) > 0:
            if all(c.isdigit() or c.lower() in 'abcdef' for c in token):
                # Check if the length of the token is within the specified range
                if 10 <= len(token) <= 90:
                    return True
        return False

    # ------------------------------------------------------------------------------------------------
    #             CREATE ENVIRONMENT VARIABLES
    # ------------------------------------------------------------------------------------------------

    def __create_env_if_no_exits__(self, key):
        print(f"ConfigHelper create_env_variables {key}")
        value = os.getenv(key, '')
        message = "OK" if self.__is_valid_secret_key__(value) else "error not a valid secret key"
        print(f"ConfigHelper key: {key} "
              f"value:{value[:25].ljust(25, ' ')} "
              f"validation:{message.upper()}")

        if message != "OK":
            print(f"ConfigHelper create {key}")
            token = secrets.token_hex(32)
            os.environ[key] = token
            value = os.getenv(key, '')
            print(f"ConfigHelper reload {key}: {value} -({token})")

    def create_env_variables(self):
        print(f"ConfigHelper create_env_variables")
        self.__create_env_if_no_exits__("SECURITY_TOKEN_KEY")
        self.__create_env_if_no_exits__("SECURITY_REFRESH_TOKEN_KEY")

    # ------------------------------------------------------------------------------------------------
    #             GET ENVIRONMENT VARIABLES
    # ------------------------------------------------------------------------------------------------

    @staticmethod
    def get_env_variables():
        data = dotenv_values(find_dotenv())
        kv = {}
        for k, v in data.items():
            if (k in ['SECURITY_TOKEN_KEY',
                      'SECURITY_REFRESH_TOKEN_KEY',
                      'LDAP_BIND_PASSWORD',
                      'DEFAULT_ADMIN_PASSWORD']):
                if len(v) > 0:
                    v = ''.ljust(8, '*')
                else:
                    v = ''
            if len(k) > 0:
                kv[k] = v
        return kv

    # ------------------------------------------------------------------------------------------------
    #             VALIDATION CONFIGS
    # ------------------------------------------------------------------------------------------------

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

    def __validate_env_variable__(self, env_var_name, var_type):
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
            # print(f"ConfigHelper key: {env_var_name.ljust(35, ' ')} "
            #       f"type:{var_type.__name__.ljust(10, ' ')} "
            #       f"value:{env_var_value.ljust(25, ' ')} "
            #       f"validation:{message.upper()}")
            self.__print_validation_key__(group="Env validation",
                                          key=env_var_name.ljust(35, ' '),
                                          key_type=var_type.__name__.ljust(10, ' '),
                                          value=env_var_value.ljust(25, ' '),
                                          message=message.upper())

            return res

    @staticmethod
    def __print_validation_key__(group='Env validation',
                                 key='',
                                 key_type='bool',
                                 value='',
                                 message=''):
        header = f"{group}".ljust(15, ' ')
        row = (f"[{header}] key:{key.ljust(35, ' ')} "
               f"type:{f'{key_type}'.ljust(10, ' ')} "
               f"value:{value[:25].ljust(25, ' ')} "
               f"validation:{message.upper()}")
        if message.upper() != "OK":
            header = 'ERROR'.ljust(10, ' ')
            # Print in red
            print(f"\033[91m{header}{row}\033[0m")
        else:
            header = 'ConfigHelper '.ljust(10, ' ')
            # print(f"\033[92m{header}{row}\033[0m")
            print(f"{header}{row}")

    @staticmethod
    def __check_integer_sequence__(text):
        # Regular expression pattern to match the format with integers greater than 0
        pattern = re.compile(r'\b([1-9]\d*):([1-9]\d*)\b')

        # Check if the pattern is found in the text
        return bool(re.search(pattern, text))

    @staticmethod
    def __is_path_exists__(path):
        return os.path.exists(path)

    def validate_env_variables(self):
        print(f"ConfigHelper Check the validity all env variables")
        block_exec = False

        nats_enable = self.nats.enable

        all_env = {'UNICORN_RELOAD': {'type': bool, 'is_mandatory': False},
                   'CONTAINER_MODE': {'type': bool, 'is_mandatory': False},
                   'K8S_IN_CLUSTER_MODE': {'type': bool, 'is_mandatory': False},
                   'K8S_VELERO_NAMESPACE': {'type': str, 'is_mandatory': False},
                   'API_ENDPOINT_PORT': {'type': int, 'is_mandatory': True},
                   'API_ENABLE_DOCUMENTATION': {'type': int, 'is_mandatory': True},
                   'API_TOKEN_EXPIRATION_MIN': {'type': int, 'is_mandatory': True},
                   'API_TOKEN_REFRESH_EXPIRATION_DAYS': {'type': int, 'is_mandatory': True},
                   'SECURITY_DISABLE_USERS_PWD_RATE': {'type': bool, 'is_mandatory': False},
                   'LIMIT_CONCURRENCY': {'type': int, 'is_mandatory': False},
                   'SCRAPY_VERSION_MIN': {'type': int, 'is_mandatory': False},
                   'NATS_ENABLE': {'type': bool, 'is_mandatory': False},
                   'NATS_PORT_CLIENT': {'type': int, 'is_mandatory': False},
                   'NATS_RETRY_REG_SEC': {'type': int, 'is_mandatory': False},
                   'NATS_ALIVE_SEC': {'type': int, 'is_mandatory': False},
                   'NATS_REQUEST_TIMEOUT_SEC': {'type': int, 'is_mandatory': False}}

        for key, value in all_env.items():
            res = self.__validate_env_variable__(key, value['type'])
            if not res and value['is_mandatory']:
                block_exec = True

        # init the dict for url keys
        urls = {'API_ENDPOINT_URL': {'protocol': False}}
        # LS 2024.07.04 add nats url
        if nats_enable:
            urls = {'NATS_ENDPOINT_URL': {'protocol': False}}

        # origins
        for x in range(1, 100, 1):
            urls[f'ORIGINS_{x}'] = {'protocol': True}

        for key, value in urls.items():
            res = os.getenv(key, None)
            if res is None or len(res) == 0:
                break
            else:
                message = "OK" if res == '*' or self.__validate_url__(res, value['protocol']) else "error not a url"
                self.__print_validation_key__(group="Env validation",
                                              key=key,
                                              key_type='url',
                                              value=res,
                                              message=message.upper())
                if message != "OK":
                    block_exec = True

        key = 'SECURITY_TOKEN_KEY'
        value = os.getenv(key, '')
        message = "OK" if self.__is_valid_secret_key__(value) else "error not a valid secret key"
        self.__print_validation_key__(group="Env validation",
                                      key=key,
                                      key_type='token',
                                      value=value[:25].ljust(25, ' '),
                                      message=message.upper())

        if message != "OK":
            block_exec = True

        key = 'SECURITY_REFRESH_TOKEN_KEY'
        value = os.getenv(key, '')
        message = "OK" if self.__is_valid_secret_key__(value) else "error not a valid secret key"

        self.__print_validation_key__(group="Env validation",
                                      key=key,
                                      key_type='token',
                                      value=value[:25].ljust(25, ' '),
                                      message=message.upper())
        if message != "OK":
            block_exec = True

        key = 'DEBUG_LEVEL'
        value = os.getenv(key, None)
        key_is_ok = False
        if value is not None:
            value = value.lower()
            key_is_ok = True if value in ['critical', 'error', 'warning', 'info', 'debug', 'trace', 'notset'] else False
        message = "OK" if key_is_ok else "error not a valid debug level"

        self.__print_validation_key__(group="Env validation",
                                      key=key,
                                      key_type='string',
                                      value=value[:25].ljust(25, ' '),
                                      message=message.upper())

        if message != "OK":
            block_exec = True

        paths = [
            # 'VELERO_CLI_PATH',
            # 'VELERO_CLI_DEST_PATH',
            'SECURITY_PATH_DATABASE']
        for key in paths:

            res = False
            value = os.getenv(key, None)
            if value is not None:
                res = self.__is_path_exists__(value)
            else:
                value = ""

            message = "OK" if res else "not valid path"

            self.__print_validation_key__(group="Path validation",
                                          key=key,
                                          key_type='path',
                                          value=value,
                                          message=message.upper())

            if not res:
                block_exec = True

        key = 'API_RATE_LIMITER_L1'
        value = os.getenv(key, None)
        message = "OK" if self.__check_integer_sequence__(value) else "error not a valid rate limiter sequence"

        self.__print_validation_key__(group="Env validation",
                                      key=key,
                                      key_type='complex',
                                      value=value[:25].ljust(25, ' '),
                                      message=message.upper())

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

                self.__print_validation_key__(group="Env validation",
                                              key=key,
                                              key_type='complex',
                                              value=value[:25].ljust(25, ' '),
                                              message=message.upper())

                if message != "OK":
                    block_exec = True

        if block_exec:
            message = f"ConfigHelper ERROR [Gen validation ] Mandatory env variables set: {not block_exec}"
            print(f"\033[91m{message}\033[0m")
            message = (
                f"ConfigHelper ERROR [Gen Validation ] !!!Warning:The application can not start. Try to update the "
                f"keys "
                f"in errors and restart the program.")
            print(f"\033[91m{message}\033[0m")
        else:
            print(f"ConfigHelper [Gen validation ] Mandatory env variables set: {not block_exec}")
        return block_exec

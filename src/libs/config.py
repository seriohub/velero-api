from dotenv import load_dotenv
import os

from helpers.handle_exceptions import handle_exceptions_instance_method


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
    def k8s_in_cluster_mode(self):
        return self.load_key('K8S_IN_CLUSTER_MODE', 'False').lower() == 'true'

    @handle_exceptions_instance_method
    def internal_debug_enable(self):
        res = self.load_key('DEBUG', 'False')
        return True if res.lower() == "true" or res.lower() == "1" else False

    @handle_exceptions_instance_method
    def logger_level(self):
        return self.load_key('LOG_LEVEL', 'info')

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

import re
import os
import requests

from core.config import ConfigHelper
from service.k8s_service import K8sService
from utils.handle_exceptions import handle_exceptions_async_method
from helpers.printer import PrintHelper

config_app = ConfigHelper()
k8sService = K8sService()


class WatchdogService:

    def __init__(self):
        self.print_ls = PrintHelper('[service.watchdog]', level=config_app.get_internal_log_level())

    @handle_exceptions_async_method
    async def online(self):
        protocol = 'http://'
        url = protocol + config_app.get_watchdog_url()
        self.print_ls.debug(f'Watchdog URL {url}')
        try:
            response = requests.get(url)
        except:
            return {'success': False, 'error': {
                'title': 'Error',
                'description': 'Check url and watchdog running'
            }}

        if response.status_code == 200:
            output = response.json()
            return {'success': True, 'data': output}

    @handle_exceptions_async_method
    async def version(self):
        protocol = 'http://'
        url = protocol + config_app.get_watchdog_url() + '/info'
        self.print_ls.debug(f'Watchdog URL {url}')
        try:
            response = requests.get(url)
        except:
            return {'success': False, 'error': {
                'title': 'Error',
                'description': 'Check url and watchdog running'
            }}

        if response.status_code == 200:
            output = response.json()
            return {'success': True, 'data': output['data']['payload']}

    @handle_exceptions_async_method
    async def send_report(self):
        protocol = 'http://'
        url = protocol + config_app.get_watchdog_url() + '/send-report'
        self.print_ls.debug(f'Watchdog URL {url}')
        try:
            response = requests.get(url)
        except:
            return {'success': False, 'error': {
                'title': 'Error',
                'description': 'Check url and watchdog running'
            }}

        if response.status_code == 200:
            output = response.json()
            return {'success': True, 'data': output['data']['payload']}

    @handle_exceptions_async_method
    async def get_env_variables(self):
        if os.getenv('K8S_IN_CLUSTER_MODE').lower() == 'true':
            output = await k8sService.get_config_map(namespace=config_app.get_k8s_velero_ui_namespace(),
                                                     configmap_name='velero-watchdog-config')
            env_data = output['data']
            return {'success': True, 'data': env_data}
        else:
            protocol = 'http://'
            url = protocol + config_app.get_watchdog_url() + '/get-config'
            self.print_ls.debug(f'Watchdog URL {url}')
            try:
                response = requests.get(url)

            except:
                return {'success': False, 'error': {
                    'title': 'Error',
                    'description': 'Check url and watchdog running'
                }}

            if response.status_code == 200:
                output = response.json()
                print(output)
                return {'success': True, 'data': output['data']['payload']}

    @handle_exceptions_async_method
    async def get_cron(self, job_name='seriohub-velero-ui-report'):

        output = await k8sService.get_cron_schedule(namespace=config_app.get_k8s_velero_ui_namespace(),
                                                    job_name=job_name)
        if output['success']:
            env_data = output['data']
            return {'success': True, 'data': env_data}
        else:
            return {'success': False, 'error': {
                'title': 'Error',
                'description': "can't read cronjob"
            }}

    @handle_exceptions_async_method
    async def send_test_notification(self,
                                     email: bool = True,
                                     telegram: bool = True,
                                     slack: bool = True):
        if not email and not telegram and not slack:
            return {'success': False, 'error': {
                'title': 'Error',
                'description': 'No notification channel is selected'
            }}
        else:
            pars = "?email=" + ('True' if email else 'False')
            pars += "&telegram=" + ('True' if telegram else 'False')
            pars += "&slack=" + ('True' if slack else 'False')

            protocol = 'http://'
            url = protocol + config_app.get_watchdog_url() + '/send-test-notification' + pars
            self.print_ls.debug(f'Watchdog URL {url}')
            try:
                response = requests.get(url)
            except:
                return {'success': False, 'error': {
                    'title': 'Error',
                    'description': 'Check url and watchdog running'
                }}

            if response.status_code == 200:
                output = response.json()
                return {'success': True, 'data': output['data']['payload']}

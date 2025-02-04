import os

import aiohttp

from core.config import ConfigHelper

from service.k8s_service import K8sService

from utils.handle_exceptions import handle_exceptions_async_method

from security.helpers.database import SessionLocal

from api.v1.schemas.update_user_config import UpdateUserConfig
from helpers.logger import ColoredLogger, LEVEL_MAPPING
import logging

db = SessionLocal()

config_app = ConfigHelper()
logger = ColoredLogger.get_logger(__name__, level=LEVEL_MAPPING.get(config_app.get_internal_log_level(), logging.INFO))
k8sService = K8sService()


def filter_dict_by_keys(input_dict, keys_to_keep):
    """
    Filters a dictionary to include only specified keys.

    :param input_dict: The original dictionary to filter.
    :param keys_to_keep: A set or list of keys to retain in the filtered dictionary.
    :return: A new dictionary containing only the specified keys.
    """
    if not isinstance(keys_to_keep, (set, list)):
        raise TypeError("keys_to_keep must be a set or list")

    return {key: value for key, value in input_dict.items() if key in keys_to_keep}


class WatchdogService:

    async def __do_api_call(self, url):
        logger.debug(f'__do_api_call URL {url}')

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        output = await response.json()
                        return {'success': True, 'data': output.get('data', {}).get('payload')}
                    else:
                        logger.error(f"[{url}] Unexpected status code: {response.status}")
                        return {'success': False, 'error': {
                            'title': 'Request Failed',
                            'description': f'HTTP {response.status}'
                        }}
        except aiohttp.ClientError as e:
            logger.error(f"[{url}] Error during async request: {e}")

            return {'success': False, 'error': {
                'title': 'Error',
                'description': 'Check URL and watchdog running'
            }}

    async def __do_api_call_post(self, url, payload):
        logger.debug(f'__do_api_call_post URL {url} Payload: {payload}')

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        output = await response.json()
                        return {'success': True, 'data': output.get('data', {}).get('payload')}
                    else:
                        logger.error(f"[{url}] Unexpected status code: {response.status}")
                        return {'success': False, 'error': {
                            'title': 'Request Failed',
                            'description': f'HTTP {response.status}'
                        }}
        except aiohttp.ClientError as e:
            logger.error(f"[{url}] Error during async request: {e}")

            return {'success': False, 'error': {
                'title': 'Error',
                'description': 'Check URL and watchdog running'
            }}

    @handle_exceptions_async_method
    async def online(self):
        protocol = 'http://'
        url = protocol + config_app.get_watchdog_url()
        logger.debug(f'Watchdog URL {url}')
        # try:
        #     response = requests.get(url)
        # except:
        #     return {'success': False, 'error': {
        #         'title': 'Error',
        #         'description': 'Check url and watchdog running'
        #     }}
        #
        # if response.status_code == 200:
        #     output = response.json()
        #     return {'success': True, 'data': output}
        return await self.__do_api_call(url)

    @handle_exceptions_async_method
    async def version(self):
        protocol = 'http://'
        url = protocol + config_app.get_watchdog_url() + '/info'
        logger.debug(f'Watchdog URL {url}')
        # try:
        #     response = requests.get(url)
        # except:
        #     return {'success': False, 'error': {
        #         'title': 'Error',
        #         'description': 'Check url and watchdog running'
        #     }}
        #
        # if response.status_code == 200:
        #     output = response.json()
        #     return {'success': True, 'data': output['data']['payload']}
        return await self.__do_api_call(url)

    @handle_exceptions_async_method
    async def send_report(self):
        # protocol = 'http://'
        # url = protocol + config_app.get_watchdog_url() + '/send-report'
        # logger.debug(f'Watchdog URL {url}')
        # try:
        #     response = requests.get(url)
        #
        # except:
        #     return {'success': False, 'error': {
        #         'title': 'Error',
        #         'description': 'Check url and watchdog running'
        #     }}
        #
        #
        # if response.status_code == 200:
        #     output = response.json()
        #     return {'success': True, 'data': output['data']['payload']}

        protocol = 'http://'
        url = protocol + config_app.get_watchdog_url() + '/send-report'
        logger.debug(f'Watchdog URL {url}')

        # try:
        #     async with aiohttp.ClientSession() as session:
        #         async with session.get(url) as response:
        #             if response.status == 200:
        #                 output = await response.json()
        #                 return {'success': True, 'data': output.get('data', {}).get('payload')}
        #             else:
        #                 logger.error(f"Unexpected status code: {response.status}")
        #                 return {'success': False, 'error': {
        #                     'title': 'Request Failed',
        #                     'description': f'HTTP {response.status}'
        #                 }}
        # except aiohttp.ClientError as e:
        #     logger.error(f"Error during async request: {e}")
        #     return {'success': False, 'error': {
        #         'title': 'Error',
        #         'description': 'Check URL and watchdog running'
        #     }}

        return await self.__do_api_call_post(url, {})

    @handle_exceptions_async_method
    async def get_env_variables(self):
        # if os.getenv('K8S_IN_CLUSTER_MODE').lower() == 'true':
        #     output = await k8sService.get_config_map(namespace=config_app.get_k8s_velero_ui_namespace(),
        #                                              configmap_name='velero-watchdog-config')
        #     env_data = output['data']
        #     return {'success': True, 'data': env_data}
        # else:
        protocol = 'http://'
        url = protocol + config_app.get_watchdog_url() + '/environment'
        # logger.debug(f'Watchdog URL {url}')
        # try:
        #     response = requests.get(url)
        # except:
        #     return {'success': False, 'error': {
        #         'title': 'Error',
        #         'description': 'Check url and watchdog running'
        #     }}
        #
        # if response.status_code == 200:
        #     output = response.json()
        #     print(output)
        #     return {'success': True, 'data': output['data']['payload']}
        return await self.__do_api_call(url)

    @handle_exceptions_async_method
    async def get_cron(self, job_name='vui-report'):

        output = await k8sService.get_watchdog_cron_schedule(namespace=config_app.get_k8s_velero_ui_namespace(),
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
                                     provider_config: str):
        if not provider_config:
            return {'success': False, 'error': {
                'title': 'Error',
                'description': 'No valid config string service is selected'
            }}
        else:

            protocol = 'http://'
            url = protocol + config_app.get_watchdog_url() + '/test-service'
            # logger.debug(f'Watchdog URL {url}')
            # try:
            #     response = requests.get(url)
            # except:
            #     return {'success': False, 'error': {
            #         'title': 'Error',
            #         'description': 'Check url and watchdog running'
            #     }}
            #
            # if response.status_code == 200:
            #     output = response.json()
            #     return {'success': True, 'data': output['data']['payload']}
            response = await self.__do_api_call_post(url, payload={'config': provider_config})
            if 'data' in response and 'success' in response['data'] and response['data']['success']:
                return {'success': True}
            else:
                return {'success': False, 'error': {
                    'title': 'Error',
                    'description': 'Services test error'
                }}

    @handle_exceptions_async_method
    async def restart(self):
        # protocol = 'http://'
        # url = protocol + config_app.get_watchdog_url() + '/restart'
        # return await self.__do_api_call_post(url, payload={})
        return await k8sService.restart_watchdog()

    @handle_exceptions_async_method
    async def get_user_configs(self):
        user_config = await k8sService.get_config_map(namespace=config_app.get_k8s_velero_ui_namespace(),
                                                      configmap_name='velero-watchdog-user-config')
        if not user_config['success']:
            user_config = {'data': {}}
        default_cm = await k8sService.get_config_map(namespace=config_app.get_k8s_velero_ui_namespace(),
                                                     configmap_name='velero-watchdog-config')

        cm = default_cm['data']
        cm.update(user_config['data'])

        return {'success': True, 'data': cm}

        #
        # user configs managed via db
        #
        # tmp = db.query(Configs).filter(
        #     Configs.module == 'watchdog', Configs.key != 'services').all()
        # if tmp:
        #     return {'success': True, 'data': {config.key: config.value for config in tmp}}
        # return {'success': False}

    @handle_exceptions_async_method
    async def update_user_configs(self, user_configs: UpdateUserConfig):

        # def add_config_prop(db, key, value):
        #     tmp = db.query(Configs).filter(
        #         Configs.module == 'watchdog', Configs.key == key).first()
        #     if tmp:
        #         tmp.value = value
        #     else:
        #         tmp = Configs(module='watchdog', key=key, value=value)
        #         db.add(tmp)
        #
        #     db.commit()
        #
        # add_config_prop(db, 'BACKUP_ENABLED', 'True' if user_configs.backupEnabled else 'False')
        # add_config_prop(db, 'SCHEDULE_ENABLED', 'True' if user_configs.scheduleEnabled else 'False')
        # add_config_prop(db, 'NOTIFICATION_SKIP_COMPLETED', 'True' if user_configs.notificationSkipCompleted else
        # 'False')
        # add_config_prop(db, 'NOTIFICATION_SKIP_DELETING', 'True' if user_configs.notificationSkipDeleting else
        # 'False')
        # add_config_prop(db, 'NOTIFICATION_SKIP_INPROGRESS', 'True' if user_configs.notificationSkipInProgress else
        # 'False')
        # add_config_prop(db, 'NOTIFICATION_SKIP_REMOVED', 'True' if user_configs.notificationSkipRemoved else 'False')
        # add_config_prop(db, 'PROCESS_CYCLE_SEC', user_configs.processCycleSeconds)
        # add_config_prop(db, 'EXPIRES_DAYS_WARNING', user_configs.expireDaysWarning)
        # add_config_prop(db, 'REPORT_BACKUP_ITEM_PREFIX', user_configs.reportBackupItemPrefix)
        # add_config_prop(db, 'REPORT_SCHEDULE_ITEM_PREFIX', user_configs.reportScheduleItemPrefix)
        default_cm = await k8sService.get_config_map(namespace=config_app.get_k8s_velero_ui_namespace(),
                                                     configmap_name='velero-watchdog-config')

        async def synckey(key: str, value):
            if value.lower() != default_cm['data'][key].lower():
                await k8sService.create_or_update_configmap(config_app.get_k8s_velero_ui_namespace(),
                                                            'velero-watchdog-user-config',
                                                            key,
                                                            value)
            else:
                await k8sService.remove_key_from_configmap(config_app.get_k8s_velero_ui_namespace(),
                                                           'velero-watchdog-user-config',
                                                           key)

        await synckey('BACKUP_ENABLED', 'True' if user_configs.backupEnabled else 'False')
        await synckey('SCHEDULE_ENABLED', 'True' if user_configs.scheduleEnabled else 'False')
        await synckey('NOTIFICATION_SKIP_COMPLETED', 'True' if user_configs.notificationSkipCompleted else 'False')
        await synckey('NOTIFICATION_SKIP_DELETING', 'True' if user_configs.notificationSkipDeleting else 'False')
        await synckey('NOTIFICATION_SKIP_INPROGRESS', 'True' if user_configs.notificationSkipInProgress else 'False')
        await synckey('NOTIFICATION_SKIP_REMOVED', 'True' if user_configs.notificationSkipRemoved else 'False')
        await synckey('PROCESS_CYCLE_SEC', str(user_configs.processCycleSeconds))
        await synckey('EXPIRES_DAYS_WARNING', str(user_configs.expireDaysWarning))
        await synckey('REPORT_BACKUP_ITEM_PREFIX', user_configs.reportBackupItemPrefix)
        await synckey('REPORT_SCHEDULE_ITEM_PREFIX', user_configs.reportScheduleItemPrefix)

        return {'success': True}

    @handle_exceptions_async_method
    async def get_user_services(self):
        # tmp = db.query(Configs).filter(
        #     Configs.module == 'watchdog', Configs.key == 'services').all()
        default_secret_content = await k8sService.get_secret(namespace=config_app.get_k8s_velero_ui_namespace(),
                                                             secret_name='velero-watchdog-config')
        user_secret_content = await k8sService.get_secret(namespace=config_app.get_k8s_velero_ui_namespace(),
                                                          secret_name='velero-watchdog-user-config')
        if user_secret_content['success']:
            apprise_config = user_secret_content['data']['APPRISE'].split(";")
        else:
            apprise_config = default_secret_content['data']['APPRISE'].split(";")

        if apprise_config:
            return {'success': True, 'data': [config.strip() for config in apprise_config]}
        return {'success': False}

    @handle_exceptions_async_method
    async def create_user_services(self, config):
        try:
            # tmp = Configs(module='watchdog',
            #               key='services',
            #               value=config)
            # db.add(tmp)
            # db.commit()
            default_secret_content = await k8sService.get_secret(namespace=config_app.get_k8s_velero_ui_namespace(),
                                                                 secret_name='velero-watchdog-config')
            user_secret_content = await k8sService.get_secret(namespace=config_app.get_k8s_velero_ui_namespace(),
                                                              secret_name='velero-watchdog-user-config')
            if not user_secret_content['success']:
                await k8sService.add_or_update_key_in_secret(namespace=config_app.get_k8s_velero_ui_namespace(),
                                                             secret_name='velero-watchdog-user-config',
                                                             key='APPRISE',
                                                             value=default_secret_content['data'][
                                                                       'APPRISE'] + ';' + config)
            else:
                await k8sService.add_or_update_key_in_secret(namespace=config_app.get_k8s_velero_ui_namespace(),
                                                             secret_name='velero-watchdog-user-config',
                                                             key='APPRISE',
                                                             value=user_secret_content['data'][
                                                                       'APPRISE'] + ';' + config)
            return {'success': True}
        except:
            return {'success': False, 'error': {
                'title': 'Error',
                'description': 'Failed create user services'
            }}

    @handle_exceptions_async_method
    async def delete_user_services(self, config):
        try:

            # Query for the existing record
            # tmp = db.query(Configs).filter_by(module='watchdog', key='services', value=config).first()
            #
            # if tmp:
            #     db.delete(tmp)
            #     db.commit()
            #     return {'success': True}
            # else:
            #     return {'success': False, 'error': {
            #         'title': 'Error',
            #         'description': 'Record not found'
            #     }}
            default_secret_content = await k8sService.get_secret(namespace=config_app.get_k8s_velero_ui_namespace(),
                                                                 secret_name='velero-watchdog-config')
            user_secret_content = await k8sService.get_secret(namespace=config_app.get_k8s_velero_ui_namespace(),
                                                              secret_name='velero-watchdog-user-config')

            if user_secret_content['success']:
                secrets = user_secret_content['data']['APPRISE'].split(";")
            else:
                secrets = default_secret_content['data']['APPRISE'].split(";")
            secrets = [secret.strip() for secret in secrets]

            secrets.remove(config)
            await k8sService.add_or_update_key_in_secret(namespace=config_app.get_k8s_velero_ui_namespace(),
                                                         secret_name='velero-watchdog-user-config',
                                                         key='APPRISE',
                                                         value=";".join(secrets))
            return {'success': True}

        except Exception as e:
            db.rollback()  # Rollback in case of an error
            return {'success': False, 'error': {
                'title': 'Error',
                'description': f'Failed to delete user services: {str(e)}'
            }}

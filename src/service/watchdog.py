import aiohttp
from fastapi import HTTPException
from kubernetes import client
from configs.config_boot import config_app
from datetime import datetime
from service.k8s import (get_watchdog_cron_schedule_service,
                         get_config_map_service,
                         create_or_update_configmap_service,
                         remove_key_from_configmap_service,
                         get_secret_service,
                         add_or_update_key_in_secret_service)

from database.db_connection import SessionLocal

from schemas.request.update_user_config import UpdateUserConfigRequestSchema

from utils.logger_boot import logger

db = SessionLocal()




# def filter_dict_by_keys(input_dict, keys_to_keep):
#     """
#     Filters a dictionary to include only specified keys.
#
#     :param input_dict: The original dictionary to filter.
#     :param keys_to_keep: A set or list of keys to retain in the filtered dictionary.
#     :return: A new dictionary containing only the specified keys.
#     """
#     if not isinstance(keys_to_keep, (set, list)):
#         raise TypeError("keys_to_keep must be a set or list")
#
#     return {key: value for key, value in input_dict.items() if key in keys_to_keep}


async def __do_api_call(url):
    logger.debug(f'__do_api_call URL {url}')

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    output = await response.json()
                    if output.get('data', {}).get('payload') is not None:
                        return output.get('data', {}).get('payload')
                    if output.get('status') is not None:
                        return output.get('status')
                else:
                    logger.error(f"[{url}] Unexpected status code: {response.status}")
                    raise HTTPException(status_code=400, detail=f'HTTP {response.status}')

    except aiohttp.ClientError as e:
        logger.error(f"[{url}] Error during async request: {e}")
        raise HTTPException(status_code=400, detail=f'Check URL and watchdog running')


async def __do_api_call_post(url, payload):
    logger.debug(f'__do_api_call_post URL {url} Payload: {payload}')

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    output = await response.json()
                    return output.get('data', {}).get('payload')
                else:
                    logger.error(f"[{url}] Unexpected status code: {response.status}")
                    raise HTTPException(status_code=400, detail=f'HTTP {response.status}')

    except aiohttp.ClientError as e:
        logger.error(f"[{url}] Error during async request: {e}")
        raise HTTPException(status_code=400, detail=f'Check URL and watchdog running')


async def check_watchdog_online_service():
    protocol = 'http://'
    url = protocol + config_app.get_watchdog_url()
    logger.debug(f'Watchdog URL {url}')
    payload = await __do_api_call(url)
    return payload


async def get_watchdog_version_service():
    protocol = 'http://'
    url = protocol + config_app.get_watchdog_url() + '/info'
    logger.debug(f'Watchdog URL {url}')
    return await __do_api_call(url)


async def send_watchdog_report():
    protocol = 'http://'
    url = protocol + config_app.get_watchdog_url() + '/send-report'
    logger.debug(f'Watchdog URL {url}')

    return await __do_api_call_post(url, {})


async def get_watchdog_env_services():
    protocol = 'http://'
    url = protocol + config_app.get_watchdog_url() + '/environment'

    return await __do_api_call(url)


async def get_watchdog_report_cron_service(job_name='vui-report'):
    output = await get_watchdog_cron_schedule_service(namespace=config_app.get_k8s_velero_ui_namespace(),
                                                      job_name=job_name)
    if output:
        env_data = output
        return env_data
    else:
        raise HTTPException(status_code=400, detail=f'Error read cronjob')


async def send_watchdog_test_notification_service(provider_config: str):
    # if not provider_config:
    #     raise HTTPException(status_code=400, detail=f"No valid config string service is selected")
    # else:

    protocol = 'http://'
    url = protocol + config_app.get_watchdog_url() + '/test-service'

    response = await __do_api_call_post(url, payload={'config': provider_config})
    print("----",response)
    if 'success' in response and response['success']:
        return True
    else:
        raise HTTPException(status_code=400, detail=f'Service Test Error')


async def restart_watchdog_service():
    try:
        namespace = config_app.get_k8s_velero_ui_namespace()
        deployment_name = "vui-watchdog"

        api_instance = client.AppsV1Api()

        deployment = api_instance.read_namespaced_deployment(name=deployment_name, namespace=namespace)

        # Update annotation in pod template (NOT just in metadata)
        restart_time = datetime.utcnow().isoformat()
        if deployment.spec.template.metadata.annotations is None:
            deployment.spec.template.metadata.annotations = {}
        deployment.spec.template.metadata.annotations["kubectl.kubernetes.io/restartedAt"] = restart_time

        # Apply the patch to update the deployment and force a restart
        api_instance.patch_namespaced_deployment(
            name=deployment_name,
            namespace=namespace,
            body={
                "spec": {"template": {"metadata": {"annotations": deployment.spec.template.metadata.annotations}}}}
        )

        return True
    except client.exceptions.ApiException as e:
        raise HTTPException(status_code=400,
                            detail=f"create cloud credentials: Exception when create cloud credentials: {e}")


async def get_watchdog_user_configs_service():
    user_config = await get_config_map_service(namespace=config_app.get_k8s_velero_ui_namespace(),
                                               configmap_name='velero-watchdog-user-config')

    if not user_config:
        user_config = {'data': {}}
    default_cm = await get_config_map_service(namespace=config_app.get_k8s_velero_ui_namespace(),
                                              configmap_name='velero-watchdog-config')

    cm = default_cm
    cm.update(user_config)

    return cm


async def update_watchdog_user_configs_service(user_configs: UpdateUserConfigRequestSchema):
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
    default_cm = await get_config_map_service(namespace=config_app.get_k8s_velero_ui_namespace(),
                                              configmap_name='velero-watchdog-config')

    async def synckey(key: str, value):
        if value.lower() != default_cm[key].lower():
            await create_or_update_configmap_service(config_app.get_k8s_velero_ui_namespace(),
                                                     'velero-watchdog-user-config',
                                                     key,
                                                     value)
        else:
            await remove_key_from_configmap_service(config_app.get_k8s_velero_ui_namespace(),
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

    return True


async def get_apprise_services():
    default_secret_content = await get_secret_service(namespace=config_app.get_k8s_velero_ui_namespace(),
                                                      secret_name='velero-watchdog-config')
    user_secret_content = await get_secret_service(namespace=config_app.get_k8s_velero_ui_namespace(),
                                                   secret_name='velero-watchdog-user-config')

    if user_secret_content:
        apprise_config = user_secret_content['APPRISE'].split(";")
    else:
        apprise_config = default_secret_content['APPRISE'].split(";")

    if apprise_config:
        return [config.strip() for config in apprise_config]
    return None


async def create_apparise_services(config):
    try:
        # tmp = Configs(module='watchdog',
        #               key='services',
        #               value=config)
        # db.add(tmp)
        # db.commit()
        default_secret_content = await get_secret_service(namespace=config_app.get_k8s_velero_ui_namespace(),
                                                          secret_name='velero-watchdog-config')
        user_secret_content = await get_secret_service(namespace=config_app.get_k8s_velero_ui_namespace(),
                                                       secret_name='velero-watchdog-user-config')
        if not user_secret_content:
            await add_or_update_key_in_secret_service(namespace=config_app.get_k8s_velero_ui_namespace(),
                                                      secret_name='velero-watchdog-user-config',
                                                      key='APPRISE',
                                                      value=default_secret_content[
                                                                'APPRISE'] + ';' + config)
        else:
            await add_or_update_key_in_secret_service(namespace=config_app.get_k8s_velero_ui_namespace(),
                                                      secret_name='velero-watchdog-user-config',
                                                      key='APPRISE',
                                                      value=user_secret_content[
                                                                'APPRISE'] + ';' + config)
        return True
    except:
        raise HTTPException(status_code=400, detail=f'Failed create apprise service')


async def delete_apprise_services(config):
    try:

        default_secret_content = await get_secret_service(namespace=config_app.get_k8s_velero_ui_namespace(),
                                                          secret_name='velero-watchdog-config')
        user_secret_content = await get_secret_service(namespace=config_app.get_k8s_velero_ui_namespace(),
                                                       secret_name='velero-watchdog-user-config')

        if user_secret_content:
            secrets = user_secret_content['APPRISE'].split(";")
        else:
            secrets = default_secret_content['APPRISE'].split(";")
        secrets = [secret.strip() for secret in secrets]

        secrets.remove(config)
        await add_or_update_key_in_secret_service(namespace=config_app.get_k8s_velero_ui_namespace(),
                                                  secret_name='velero-watchdog-user-config',
                                                  key='APPRISE',
                                                  value=";".join(secrets))
        return True

    except Exception as e:
        db.rollback()  # Rollback in case of an error
        raise HTTPException(status_code=400, detail=f'Failed to delete apprise services: {str(e)}')

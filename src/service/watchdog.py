import aiohttp
from fastapi import HTTPException
from kubernetes import client
from vui_common.configs.config_proxy import config_app
from datetime import datetime
from service.k8s_secret import get_secret_service, add_or_update_key_in_secret_service
from vui_common.service.k8s import get_config_map_service
from service.k8s_configmap import (create_or_update_configmap_service,
                                   remove_key_from_configmap_service)

from schemas.request.update_user_config import UpdateUserConfigRequestSchema
from vui_common.utils.k8s_tracer import trace_k8s_async_method

from vui_common.logger.logger_proxy import logger
from constants.watchdog import ENVIRONMENT


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
        # raise HTTPException(status_code=400, detail=f'Check URL and watchdog running')
        raise RuntimeError("Http Error")


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


@trace_k8s_async_method(description="Check watchdog online")
async def check_watchdog_online_service():
    protocol = 'http://'
    url = protocol + config_app.watchdog.url
    logger.debug(f'Watchdog URL {url}')
    payload = await __do_api_call(url)
    return payload


@trace_k8s_async_method(description="Get watchdog version")
async def get_watchdog_version_service():
    protocol = 'http://'
    url = protocol + config_app.watchdog.url + '/info'
    logger.debug(f'Watchdog URL {url}')
    return await __do_api_call(url)


@trace_k8s_async_method(description="Get watchdog environment")
async def get_watchdog_env_services():
    protocol = 'http://'
    url = protocol + config_app.watchdog.url + '/environment'

    watchdog_env = await __do_api_call(url)
    filtered_kv = {k: v for k, v in watchdog_env.items() if k in ENVIRONMENT}

    return filtered_kv


@trace_k8s_async_method(description="Get watchdog cron")
async def get_watchdog_report_cron_service(job_name='vui-report'):
    try:
        api_instance = client.BatchV1Api()
        logger.debug(f"namespace {config_app.k8s.velero_namespace} job_name {job_name}")
        cronjob = api_instance.read_namespaced_cron_job(name=job_name,
                                                        namespace=config_app.k8s.vui_namespace)
        cron_schedule = cronjob.spec.schedule
        return cron_schedule

    except Exception as e:
        logger.error(f"Error get cronjob '{job_name}': {e}")
        raise HTTPException(status_code=400, detail=f"Error get cronjob '{job_name}': {e}")


@trace_k8s_async_method(description="Restart watchdog")
async def restart_watchdog_service():
    try:
        namespace = config_app.k8s.vui_namespace
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


# ------------------------------------------------------------------------------------------------
#             USER CONFIG
# ------------------------------------------------------------------------------------------------
async def get_watchdog_user_configs_service():
    user_config = await get_config_map_service(namespace=config_app.k8s.vui_namespace,
                                               configmap_name='vui-watchdog-user-config')

    if not user_config:
        user_config = {'data': {}}
    default_cm = await get_config_map_service(namespace=config_app.k8s.vui_namespace,
                                              configmap_name='vui-watchdog-config')

    cm = default_cm
    cm.update(user_config)

    return cm


async def update_watchdog_user_configs_service(user_configs: UpdateUserConfigRequestSchema):
    default_cm = await get_config_map_service(namespace=config_app.k8s.vui_namespace,
                                              configmap_name='vui-watchdog-config')

    async def synckey(key: str, value):
        if value.lower() != default_cm[key].lower():
            await create_or_update_configmap_service(config_app.k8s.vui_namespace,
                                                     'vui-watchdog-user-config',
                                                     key,
                                                     value)
        else:
            await remove_key_from_configmap_service(config_app.k8s.vui_namespace,
                                                    'vui-watchdog-user-config',
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


# ------------------------------------------------------------------------------------------------
#
#             NOTIFICATION
#
# ------------------------------------------------------------------------------------------------

@trace_k8s_async_method(description="Send watchdog report")
async def send_watchdog_report():
    protocol = 'http://'
    url = protocol + config_app.watchdog.url + '/send-report'
    logger.debug(f'Watchdog URL {url}')

    return await __do_api_call_post(url, {})


@trace_k8s_async_method(description="Test watchdog notification service")
async def send_watchdog_test_notification_service(provider_config: str):
    protocol = 'http://'
    url = protocol + config_app.watchdog.url + '/test-service'

    response = await __do_api_call_post(url, payload={'config': provider_config})

    if 'success' in response and response['success']:
        return True
    else:
        raise HTTPException(status_code=400, detail=f'Service Test Error')


# ------------------------------------------------------------------------------------------------
#             APPRISE CONFIGS
# ------------------------------------------------------------------------------------------------

async def get_apprise_services():
    default_secret_content = await get_secret_service(namespace=config_app.k8s.vui_namespace,
                                                      secret_name='vui-watchdog-secret')
    user_secret_content = await get_secret_service(namespace=config_app.k8s.vui_namespace,
                                                   secret_name='velero-watchdog-user-secret')

    if user_secret_content:
        apprise_config = user_secret_content['APPRISE'].split(";")
    else:
        apprise_config = default_secret_content['APPRISE'].split(";")

    if apprise_config:
        return [config.strip() for config in apprise_config]
    return None


async def create_apparise_services(config):
    try:
        default_secret_content = await get_secret_service(namespace=config_app.k8s.vui_namespace,
                                                          secret_name='vui-watchdog-secret')
        user_secret_content = await get_secret_service(namespace=config_app.k8s.vui_namespace,
                                                       secret_name='velero-watchdog-user-secret')
        if not user_secret_content:
            await add_or_update_key_in_secret_service(namespace=config_app.k8s.vui_namespace,
                                                      secret_name='velero-watchdog-user-secret',
                                                      key='APPRISE',
                                                      value=default_secret_content[
                                                                'APPRISE'] + ';' + config)
        else:
            await add_or_update_key_in_secret_service(namespace=config_app.k8s.vui_namespace,
                                                      secret_name='velero-watchdog-user-secret',
                                                      key='APPRISE',
                                                      value=user_secret_content[
                                                                'APPRISE'] + ';' + config)
        return True
    except:
        raise HTTPException(status_code=400, detail=f'Failed create apprise service')


async def delete_apprise_services(config):
    try:

        default_secret_content = await get_secret_service(namespace=config_app.k8s.vui_namespace,
                                                          secret_name='vui-watchdog-secret')
        user_secret_content = await get_secret_service(namespace=config_app.k8s.vui_namespace,
                                                       secret_name='velero-watchdog-user-secret')

        if user_secret_content:
            secrets = user_secret_content['APPRISE'].split(";")
        else:
            secrets = default_secret_content['APPRISE'].split(";")
        secrets = [secret.strip() for secret in secrets]

        secrets.remove(config)
        await add_or_update_key_in_secret_service(namespace=config_app.k8s.vui_namespace,
                                                  secret_name='velero-watchdog-user-secret',
                                                  key='APPRISE',
                                                  value=";".join(secrets))
        return True

    except Exception as e:
        raise HTTPException(status_code=400, detail=f'Failed to delete apprise services: {str(e)}')

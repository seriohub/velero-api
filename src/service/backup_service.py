import os
import shutil
import json
import re
from kubernetes import client, config

from core.config import ConfigHelper

from utils.commons import filter_in_progress, add_id_to_list, logs_string_to_list, parse_create_parameters, extract_path
from utils.process import run_process_check_output, run_process_check_call
from utils.handle_exceptions import handle_exceptions_async_method

from helpers.printer import PrintHelper
from utils.commons import convert_to_list
from service.k8s_service import K8sService

from service.backup_location_service import BackupLocationService
from service.snapshot_location_service import SnapshotLocationService


k8sService = K8sService()
backupLocation = BackupLocationService()
snapshotLocation = SnapshotLocationService()
config_app = ConfigHelper()


class BackupService:

    def __init__(self):

        if os.getenv('K8S_IN_CLUSTER_MODE').lower() == 'true':
            config.load_incluster_config()
        else:
            self.kube_config_file = os.getenv('KUBE_CONFIG_FILE')
            config.load_kube_config(config_file=self.kube_config_file)

        self.client_core_v1_api = client.CoreV1Api()
        self.client_custom_objects_api = client.CustomObjectsApi()
        self.print_ls = PrintHelper('[service.backup]', level=config_app.get_internal_log_level())

    def __filter_last_backup_for_every_schedule(self, data):
        result = {}

        for item in data:
            if 'labels' in item['metadata'] and 'velero.io/schedule-name' in item['metadata']['labels']:
                schedule_name = item['metadata']['labels']['velero.io/schedule-name']
                creation_timestamp = item['metadata']['creationTimestamp']

                if schedule_name in result:
                    if creation_timestamp > result[schedule_name]['metadata']['creationTimestamp']:
                        result[schedule_name] = item
                else:
                    result[schedule_name] = item

        return list(result.values())

    @handle_exceptions_async_method
    async def check_expiration(self, expiration):
        pattern = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$')
        return bool(pattern.match(expiration))

    @handle_exceptions_async_method
    async def get_settings_create(self):
        namespaces = (await k8sService.get_ns())['data']
        backup_location = (await backupLocation.get())['data']
        snapshot_location = (await snapshotLocation.get())['data']
        backup_location_list = [item['metadata']['name'] for item in backup_location if
                                'metadata' in item and 'name' in item['metadata']]
        snapshot_location_list = [item['metadata']['name'] for item in snapshot_location if
                                  'metadata' in item and 'name' in item['metadata']]
        valid_resources = (await k8sService.get_resources())['data']

        output = {'namespaces': namespaces,
                  'backup_location': backup_location_list,
                  'snapshot_location': snapshot_location_list,
                  'resources': valid_resources
                  }

        return {'success': True, 'data': output}

    @handle_exceptions_async_method
    async def get(self, schedule_name=None, only_last_for_schedule=False, in_progress=False, publish_message=True):
        output = await run_process_check_output(['velero', 'backup', 'get', '-o', 'json',
                                                 '-n', os.getenv('K8S_VELERO_NAMESPACE', 'velero')],
                                                publish_message=publish_message)
        if not output['success']:
            return output

        backups = json.loads(output['data'])
        backups = convert_to_list(backups)

        if schedule_name is not None:
            backups['items'] = [x for x in backups['items'] if
                                'velero.io/schedule-name' in x['metadata']['labels'] and x['metadata']['labels'][
                                    'velero.io/schedule-name'] == schedule_name]

        if only_last_for_schedule:
            backups['items'] = self.__filter_last_backup_for_every_schedule(backups['items'])

        if in_progress:
            backups['items'] = filter_in_progress(backups['items'])

        add_id_to_list(backups['items'])

        return {'success': True, 'data': backups['items']}

    @handle_exceptions_async_method
    async def logs(self, backup_name):

        output = await run_process_check_output(['velero', 'backup', 'logs', backup_name,
                                                 '-n', os.getenv('K8S_VELERO_NAMESPACE', 'velero')])
        if not output['success']:
            return output

        return {'success': True, 'data': logs_string_to_list(output['data'])}

    @handle_exceptions_async_method
    async def describe(self, backup_name):

        output = await run_process_check_output(['velero', 'backup', 'describe', backup_name,
                                                 '--colorized=false', '--details', '-o', 'json',
                                                 '-n', os.getenv('K8S_VELERO_NAMESPACE', 'velero')])
        if not output['success']:
            return output

        return {'success': True, 'data': json.loads(output['data'])}

    @handle_exceptions_async_method
    async def delete(self, backup_name):

        output = await run_process_check_call(['velero', 'backup', 'delete', backup_name, '--confirm',
                                               '-n', os.getenv('K8S_VELERO_NAMESPACE', 'velero')])
        if not output['success']:
            return output

        return {'success': True}

    @handle_exceptions_async_method
    async def create(self, info):

        cmd = ['velero', 'backup', 'create', info.name,
               '-n', os.getenv('K8S_VELERO_NAMESPACE', 'velero')]

        cmd += parse_create_parameters(info)

        output = await run_process_check_call(cmd)
        if not output['success']:
            return output

        return {'success': True}

    @handle_exceptions_async_method
    async def create_from_schedule(self, info):
        cmd = ['velero', 'backup', 'create', '--from-schedule', info['scheduleName'],
               '-n', os.getenv('K8S_VELERO_NAMESPACE', 'velero')]

        output = await run_process_check_call(cmd)
        if not output['success']:
            return output

        return {'success': True}

    @handle_exceptions_async_method
    async def update_expiration(self, backup_name, expiration):

        api_instance = self.client_custom_objects_api

        # params
        #  update fix 'velero' with env variable
        namespace = config_app.get_k8s_velero_namespace()
        resource = 'backups'

        # get backup object
        backup = api_instance.get_namespaced_custom_object(
            group='velero.io',
            version='v1',
            namespace=namespace,
            plural=resource,
            name=backup_name,
        )

        # edit ttl field
        backup['status']['expiration'] = expiration

        # update ttl field
        api_instance.replace_namespaced_custom_object(
            group='velero.io',
            version='v1',
            namespace=namespace,
            plural=resource,
            name=backup_name,
            body=backup,
        )

        return {'success': True}

    @handle_exceptions_async_method
    async def get_expiration(self, backup_name):

        api_instance = self.client_custom_objects_api

        # params
        # LS 2024.02.21 update fix 'velero' with env variable
        # namespace = 'velero'
        namespace = config_app.get_k8s_velero_namespace()

        resource = 'backups'

        # get backup object
        backup = api_instance.get_namespaced_custom_object(
            group="velero.io",
            version="v1",
            namespace=namespace,
            plural=resource,
            name=backup_name,
        )
        return {'success': True, 'data': backup['status']['expiration']}

    @handle_exceptions_async_method
    async def get_backup_storage_classes(self, backup_name):

        # get tmp folder
        tmp_folder = os.getenv('DOWNLOAD_TMP_FOLDER', '/tmp/velero-api')
        if not (os.path.exists(tmp_folder)):
            os.mkdir(tmp_folder)
        # delete if exists old data in tmp folder
        path = os.path.join(tmp_folder, backup_name + '-data.tar.gz')
        if os.path.exists(path):
            os.remove(path)
        path = os.path.join(tmp_folder, backup_name)
        if os.path.exists(path):
            shutil.rmtree(path)
        # download all kubernetes manifests for a backup
        cmd = ['velero', 'backup', 'download', backup_name,
               '-n', os.getenv('K8S_VELERO_NAMESPACE', 'velero')]

        output = await run_process_check_output(cmd, cwd=tmp_folder)
        if not output['success']:
            return output

        # extract manifests from tar.gz
        path = extract_path(output['data'])
        self.print_ls.debug("path to extract: " + path)
        filename = os.path.basename(path)

        os.mkdir(os.path.join(tmp_folder, backup_name))
        cmd = ['tar', 'xf', filename, '-C', backup_name]
        output = await run_process_check_output(cmd, cwd=tmp_folder)
        if not output['success']:
            return output

        # extract pvc data
        persistent_volume_claims = os.path.join(tmp_folder, backup_name, 'resources', 'persistentvolumeclaims', 'namespaces')

        backup_storage_classes = []
        if os.path.isdir(persistent_volume_claims):
            for folder_name in os.listdir(persistent_volume_claims):
                folder_path = os.path.join(persistent_volume_claims, folder_name)
                # Check if the current item is a directory
                if os.path.isdir(folder_path):
                    for filename in os.listdir(folder_path):
                        f = os.path.join(persistent_volume_claims, folder_name, filename)
                        # checking if it is a file
                        if os.path.isfile(f):
                            f = open(f)
                            data = json.load(f)
                            backup_storage_classes.append(json.loads(
                                data['metadata']['annotations']['kubectl.kubernetes.io/last-applied-configuration']))
                            f.close()

        return {'success': True, 'data': backup_storage_classes}

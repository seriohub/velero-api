import os
from kubernetes import client, config
import shutil
import json
from fastapi.responses import JSONResponse

from libs.process import *
from libs.k8s import K8s
from libs.backup_location import BackupLocation
from libs.snapshot_location import SnapshotLocation
from libs.config import ConfigEnv
from helpers.commons import *
from helpers.json_response import *
from helpers.printer_helper import PrintHelper

k8sv1 = K8s()
backupLocation = BackupLocation()
snapshotLocation = SnapshotLocation()
config_app = ConfigEnv()


class Backup:

    def __init__(self):

        if os.getenv('K8S_IN_CLUSTER_MODE').lower() == 'true':
            config.load_incluster_config()
        else:
            self.kube_config_file = os.getenv('KUBE_CONFIG_FILE')
            config.load_kube_config(config_file=self.kube_config_file)

        self.client_core_v1_api = client.CoreV1Api()
        self.client_custom_objects_api = client.CustomObjectsApi()
        self.print_ls = PrintHelper('[libs/backup]')

    @handle_exceptions_instance_method
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

    @handle_exceptions_instance_method
    async def get_settings_create(self):
        namespaces = await k8sv1.get_ns()
        backup_location = await backupLocation.get(json_response=False)
        snapshot_location = await snapshotLocation.get(json_response=False)
        backup_location_list = [item['metadata']['name'] for item in backup_location['items'] if 'metadata' in item and 'name' in item['metadata']]
        snapshot_location_list = [item['metadata']['name'] for item in snapshot_location['items'] if 'metadata' in item and 'name' in item['metadata']]

        res = {'namespaces': namespaces,
               'backup_location': backup_location_list,
               'snapshot_location': snapshot_location_list
               # TODO: get all resource for populate multiselect in front end form
               # 'resources': k8sv1.get_resources()
               }
        return {'data': {'payload': res}}

    @handle_exceptions_async_method
    async def get(self, schedule_name=None, only_last_for_schedule=False, json_response=True, in_progress=False, publish_message=True):
        output = await run_process_check_output(['velero', 'backup', 'get', '-o', 'json'], publish_message=publish_message)
        if 'error' in output:
            return JSONResponse(content=output['error'].toJSON(), status_code=400)

        backups = json.loads(output['data'])

        # if backups['kind'].lower() == 'restore':
        #     backups = {'items': [backups]}

        if schedule_name is not None:
            backups['items'] = [x for x in backups['items'] if
                                'velero.io/schedule-name' in x['metadata']['labels'] and x['metadata']['labels'][
                                    'velero.io/schedule-name'] == schedule_name]

        if only_last_for_schedule:
            backups['items'] = self.__filter_last_backup_for_every_schedule(backups['items'])

        if in_progress:
            backups['items'] = filter_in_progress(backups['items'])

        add_id_to_list(backups['items'])

        response = SuccessfulRequest()
        response.data = backups['items']

        if json_response:
            return JSONResponse(content=response.toJSON(), status_code=200)
        else:
            return backups

    @handle_exceptions_async_method
    async def logs(self, backup_name):
        if not backup_name:
            return {'error': {'title': 'Error',
                              'description': 'Backup name is required'
                              }
                    }

        output = await run_process_check_output(['velero', 'backup', 'logs', backup_name])
        if 'error' in output:
            return output

        res = {'data': {'payload': logs_string_to_list(output['data'])}}
        return JSONResponse(content=res, status_code=201, headers={'X-Custom-Header': 'header-value'})

    @handle_exceptions_async_method
    async def describe(self, backup_name):
        if not backup_name:
            return {'error': {'title': 'Error',
                              'description': 'Backup name is required'
                              }
                    }

        output = await run_process_check_output(['velero', 'backup', 'describe', backup_name, '--colorized=false', '--details', '-o', 'json'])

        if 'error' in output:
            return output

        output = json.loads(output['data'])

        return {'data': {'payload': output}}

    @handle_exceptions_async_method
    async def delete(self, backup_name):
        if not backup_name:
            return {'error': {'title': 'Error',
                              'description': 'Backup name is required'
                              }
                    }

        output = await run_process_check_call(['velero', 'backup', 'delete', backup_name, '--confirm'])
        if 'error' in output:
            return output

        return {'messages': [{'title': 'Delete backup',
                              'description': f"Backup {backup_name} deleted request done!",
                              'type': 'info'
                              }
                             ]
                }

    @handle_exceptions_async_method
    async def create(self, info):

        if not info['values']['name'] or info['values']['name'] == '':
            return {'error': {'title': 'Error',
                              'description': 'Backup name is required'
                              }
                    }
        cmd = ['velero', 'backup', 'create', info['values']['name']]

        cmd += parse_create_parameters(info)

        output = await run_process_check_call(cmd)
        if 'error' in output:
            return output

        return {'messages': [{'title': 'Create backup',
                              'description': f"Backup { info['values']['name']} created!",
                              'type': 'info'
                              }
                             ]
                }

    @handle_exceptions_async_method
    async def create_from_schedule(self, info):

        if not info['scheduleName'] or info['scheduleName'] == '':
            return {'error': {'title': 'Error',
                              'description': 'Schedule name name is required'
                              }
                    }
        cmd = ['velero', 'backup', 'create', '--from-schedule', info['scheduleName']]
        output = await run_process_check_call(cmd)
        if 'error' in output:
            return output

        return {'messages': [{'title': 'Create backup',
                              'description': f"Backup from schedule {info['scheduleName']} created!",
                              'type': 'info'
                              }]
                }

    @handle_exceptions_instance_method
    def check_ttl(self, ttl):
        # check ttl format
        pattern = re.compile(r'^\d+h\d+m\d+s$')
        return bool(pattern.match(ttl))

    @handle_exceptions_instance_method
    def check_expiration(self, expiration):
        pattern = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$')
        return bool(pattern.match(expiration))

    @handle_exceptions_async_method
    async def update_expiration(self, backup_name, expiration):
        if not backup_name or not expiration:
            return {'error': {'title': 'Error',
                              'description': 'Backup name and expiration are required'
                              }
                    }

        if not self.check_expiration(expiration):
            return {'error': {'title': 'Error',
                              'description': 'Check expiration format'
                              }
                    }

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

        return {'messages': [{'title': 'TTL Updated',
                              'description': f"Backup {backup_name} expiration updated!",
                              'type': 'info'
                              }]
                }

    @handle_exceptions_async_method
    async def get_expiration(self, backup_name):
        if not backup_name:
            return {'error': {'title': 'Error',
                              'description': 'Backup name is required'
                              }
                    }

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

        return {'data': {'payload':
                         {'expiration': backup['status']['expiration']}
                         }
                }

    @handle_exceptions_async_method
    async def get_backup_storage_classes(self, backup_name):
        if not backup_name:
            return {'error': {'title': 'Error',
                              'description': 'Backup name is required'
                              }
                    }
        # get tmp folder
        tmp_folder = 'tmp'
        if not (os.path.exists(tmp_folder)):
            os.mkdir(tmp_folder)
        # delete if exists old data in tmp folder
        path = os.path.join('.', tmp_folder, backup_name + '-data.tar.gz')
        if os.path.exists(path):
            os.remove(path)
        path = os.path.join('.', tmp_folder, backup_name)
        if os.path.exists(path):
            shutil.rmtree(path)

        # download all kubenretes manifests for a backup
        cmd = ['velero', 'backup', 'download',  backup_name]
        output = await run_process_check_output(cmd, cwd=tmp_folder)
        if 'error' in output:
            return output

        # extract manifests from tar.gz
        path = extract_path(output['data'])
        self.print_ls.debug("path to extract: " + path)
        filename = os.path.basename(path)
        if 'error' in output:
            return output

        os.mkdir(os.path.join('.', tmp_folder, backup_name))
        cmd = ['tar', 'xf', filename, '-C', backup_name]
        output = await run_process_check_output(cmd, cwd=tmp_folder)
        if 'error' in output:
            return output

        # extract pvc data
        persistent_volume_claims = os.path.join('.', tmp_folder, backup_name, 'resources', 'persistentvolumeclaims', 'namespaces')

        backup_storage_classes = []
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
                        backup_storage_classes.append(json.loads(data['metadata']['annotations']['kubectl.kubernetes.io/last-applied-configuration']))
                        f.close()

        return {'data': backup_storage_classes}

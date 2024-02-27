import json
import os
import shlex

from utils.commons import filter_in_progress, add_id_to_list, logs_string_to_list
from utils.process import run_process_check_output, run_process_check_call
from utils.handle_exceptions import handle_exceptions_async_method


class RestoreService:

    @handle_exceptions_async_method
    async def get(self, in_progress=False, publish_message=True):
        output = await run_process_check_output(['velero', 'restore', 'get', '-o', 'json',
                                                 '-n', os.getenv('K8S_VELERO_NAMESPACE', 'velero')],
                                                publish_message=publish_message)
        if not output['success']:
            return output

        restores = json.loads(output['data'])

        if restores['kind'].lower() == 'restore':
            restores = {'items': [restores]}

        if in_progress:
            restores['items'] = filter_in_progress(restores['items'])

        add_id_to_list(restores['items'])

        return {'success': True, 'data': restores['items']}

    @handle_exceptions_async_method
    async def create(self, req_info):

        backup_name = req_info['resource_name']
        mapping_namespaces = req_info['mapping_namespaces']
        optional_parameters = req_info['parameters']
        cmd = ['velero', 'restore', 'create', '--from-backup', backup_name,
               '-n', os.getenv('K8S_VELERO_NAMESPACE', 'velero')]
        if len(mapping_namespaces) > 0:
            dict_str = ",".join(":".join([key, str(value)])
                                for key, value in mapping_namespaces.items())
            cmd += ['--namespace-mappings', dict_str]
        cmd.extend(shlex.split(optional_parameters or ''))

        output = await run_process_check_output(cmd)
        if not output['success']:
            return output

        return {'success': True}

    @handle_exceptions_async_method
    async def logs(self, restore_name):

        output = await run_process_check_output(['velero', 'restore', 'logs', restore_name,
                                                 '-n', os.getenv('K8S_VELERO_NAMESPACE', 'velero')])
        if not output['success']:
            return output

        return {'success': True, 'data': logs_string_to_list(output['data'])}

    @handle_exceptions_async_method
    async def describe(self, restore_name):

        output = await run_process_check_output(
            ['velero', 'restore', 'describe', restore_name, '--colorized=false', '--details',
             '-n', os.getenv('K8S_VELERO_NAMESPACE', 'velero')])

        if not output['success']:
            return output

        return {'success': True, 'data': output['data']}

    @handle_exceptions_async_method
    async def delete(self, restore_name):

        output = await run_process_check_call(['velero', 'restore', 'delete', restore_name, '--confirm',
                                               '-n', os.getenv('K8S_VELERO_NAMESPACE', 'velero')])
        if not output['success']:
            return output

        return {'success': True, 'data': output['data']}

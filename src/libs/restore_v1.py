import json
import shlex
from fastapi.responses import JSONResponse

from libs.process_v1 import *

from helpers.commons import *
from helpers.handle_exceptions import *


class RestoreV1:

    @handle_exceptions_async_method
    async def get(self, json_response=True, in_progress=False, publish_message=True):
        output = await run_process_check_output(['velero', 'restore', 'get', '-o', 'json'], publish_message=publish_message)
        if 'error' in output:
            return output

        restores = json.loads(output['data'])

        if restores['kind'].lower() == 'restore':
            restores = {'items': [restores]}

        if in_progress:
            restores['items'] = filter_in_progress(restores['items'])

        add_id_to_list(restores['items'])

        res = {'data': {'payload': restores}}

        if json_response:
            return JSONResponse(content=res, status_code=201, headers={'X-Custom-Header': 'header-value'})
        else:
            return restores

    @handle_exceptions_instance_method
    async def create(self, req_info):

        resource_type = req_info["resource_type"]
        backup_name = req_info["resource_name"]

        if backup_name == '':
            res = {'error': 'Invalid request. You can only provide a backup name.'}
            return JSONResponse(content=res, status_code=201, headers={'X-Custom-Header': 'header-value'})

        if not is_valid_name(backup_name):
            res = {'error', 'Invalid resource name.'}
            return JSONResponse(content=res, status_code=201, headers={'X-Custom-Header': 'header-value'})

        optional_parameters = req_info['parameters']
        cmd = ['velero', 'restore', 'create', '--from-backup', backup_name]
        cmd.extend(shlex.split(optional_parameters or ''))

        output = await run_process_check_output(cmd)
        if 'error' in output:
            return output

        return {
            "messages": [{
                'title': f"Restore",
                'description': f"Restore from {resource_type} {backup_name} created successfully",
                'type': 'info'}
            ]
        }

    @handle_exceptions_instance_method
    async def logs(self, restore_name):
        if not restore_name:
            return {'error': {'title': 'Error',
                              'description': 'Restore name is required'
                              }
                    }

        output = await run_process_check_output(['velero', 'restore', 'logs', restore_name])
        if 'error' in output:
            return output

        res = {'data': {'payload': logs_string_to_list(output['data'])}}
        return JSONResponse(content=res, status_code=201, headers={'X-Custom-Header': 'header-value'})

    @handle_exceptions_instance_method
    async def describe(self, restore_name):
        if not restore_name:
            return {'error': {'title': 'Error',
                              'description': 'Restore name is required'
                              }
                    }

        output = await run_process_check_output(['velero', 'restore', 'describe', restore_name, '--colorized=false', '--details'])

        if 'error' in output:
            return output

        return {'data': {'payload': output}}

    @handle_exceptions_instance_method
    async def delete(self, restore_name):
        if not restore_name:
            return {'error': {'title': 'Error',
                              'description': 'Restore name is required'
                              }
                    }

        output = await run_process_check_call(['velero', 'restore', 'delete', restore_name, '--confirm'])
        if 'error' in output:
            return output

        return {'messages': [{'title': 'Delete restore',
                              'description': f"Restore {restore_name} deleted request done!",
                              'type': 'info'
                              }]
                }

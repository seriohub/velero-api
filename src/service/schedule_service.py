import json
import os

from utils.process import run_process_check_output, run_process_check_call
from utils.commons import add_id_to_list, parse_create_parameters
from utils.handle_exceptions import handle_exceptions_async_method


class ScheduleService:

    def __init(self):
        pass

    @handle_exceptions_async_method
    async def get(self,):
        output = await run_process_check_output(['velero', 'schedule', 'get', '-o', 'json',
                                                 '-n', os.getenv('K8S_VELERO_NAMESPACE', 'velero')])
        if not output['success']:
            return output

        schedules = json.loads(output['data'])

        add_id_to_list(schedules['items'])

        return {'success': True, 'data': schedules['items']}

    @handle_exceptions_async_method
    async def describe(self, schedule_name):

        output = await run_process_check_output(['velero', 'schedule', 'describe', schedule_name, '--colorized=false',
                                                 '-n', os.getenv('K8S_VELERO_NAMESPACE', 'velero')])
        if not output['success']:
            return output

        return {'success': True, 'data': output['data']}

    @handle_exceptions_async_method
    async def pause(self, schedule_name):

        output = await run_process_check_call(['velero', 'schedule', 'pause', schedule_name,
                                               '-n', os.getenv('K8S_VELERO_NAMESPACE', 'velero')])
        if not output['success']:
            return output

        return {'success': True}

    @handle_exceptions_async_method
    async def unpause(self, schedule_name):

        output = await run_process_check_call(['velero', 'schedule', 'unpause', schedule_name,
                                               '-n', os.getenv('K8S_VELERO_NAMESPACE', 'velero')])

        if not output['success']:
            return output

        return {'success': True}

    @handle_exceptions_async_method
    async def create(self, info):

        cmd = ['velero', 'schedule', 'create', info.name,
               '-n', os.getenv('K8S_VELERO_NAMESPACE', 'velero')]

        cmd += parse_create_parameters(info)

        output = await run_process_check_call(cmd)
        if not output['success']:
            return output

        return {'success': True}

    @handle_exceptions_async_method
    async def delete(self, schedule_name):

        output = await run_process_check_call(['velero', 'schedule', 'delete', schedule_name, '--confirm',
                                               '-n', os.getenv('K8S_VELERO_NAMESPACE', 'velero')])
        if not output['success']:
            return output

        return {'success': True}

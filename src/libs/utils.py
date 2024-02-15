import re
from fastapi.responses import JSONResponse

from libs.backup import Backup
from libs.config import ConfigEnv
from libs.restore import Restore
from libs.schedule import Schedule
from libs.k8s import K8s
from libs.process import *

from helpers.handle_exceptions import *


backup = Backup()
restore = Restore()
schedule = Schedule()
k8s = K8s()
config_app = ConfigEnv()


class Utils:

    @handle_exceptions_instance_method
    def _resources_stats(self, resources, count_from_schedule=False):
        count = len(resources)

        completed = [x for x in resources if 'status' in x and 'phase' in x['status'] and x['status']['phase'] == 'Completed']
        completed_count = len(completed)

        partial_failed = [x for x in resources if 'status' in x and 'phase' in x['status'] and x['status']['phase'] == 'PartiallyFailed']
        partial_failed_count = len(partial_failed)

        failed = [x for x in resources if 'status' in x and 'phase' in x['status'] and x['status']['phase'] == 'Failed']
        failed_count = len(failed)

        scheduled = [x for x in resources if 'labels' in x['metadata'] and 'velero.io/schedule-name' in x['metadata']['labels']]
        scheduled_count = len(scheduled)

        res = {'count': count,
               # 'from_schedule_count': scheduled_count,
               'stats': [{'label': 'Completed',
                          'count': completed_count,
                          'perc': round(100 * completed_count/count if count > 0 else 0 , 2),
                          'color': 'green'
                          },
                         {'label': 'Partial Failed',
                          'count': partial_failed_count,
                          'perc': round(100 * partial_failed_count / count  if count > 0 else 0, 2),
                          'color': 'orange'
                          },
                         {'label': 'Failed',
                          'count': failed_count,
                          'perc': round(100 * failed_count / count  if count > 0 else 0, 2),
                          'color': 'red'
                          }]
               }
        if count_from_schedule:
            res['from_schedule_count'] = scheduled_count
        return res

    @handle_exceptions_instance_method
    def _schedules_stats(self, resources):
        count = len(resources)

        paused = [x for x in resources if 'paused' in x['spec']]

        paused_count = len(paused)

        unpaused_count = count - paused_count

        res = {'count': count,
               'from_schedule_count': 0,
               'stats': [
                   {'label': 'Unpaused',
                    'count': unpaused_count,
                    'perc': round(100 * unpaused_count / count if count > 0 else 0, 2),
                    'color': 'green'
                    },
                   {'label': 'Paused',
                    'count': paused_count,
                    'perc': round(100 * paused_count/count if count > 0 else 0, 2),
                    'color': 'red'
                    }]
               }
        return res

    @handle_exceptions_instance_method
    def _get_all_scheduled_namespace(self, scheduled):

        unique_values_set = set()

        for item in scheduled:
            include_namespaces = item.get('spec', {}).get('template', {}).get('includedNamespaces', [])
            unique_values_set.update(include_namespaces)

        unique_values_list = list(unique_values_set)
        return unique_values_list

    @handle_exceptions_instance_method
    def get_completion_timestamp(self, item):
        return item['status'].get('completionTimestamp', str('-'))

    @handle_exceptions_async_method
    async def stats(self):

        backups = await backup.get(json_response=False)
        all_backups_stats = self._resources_stats(backups['items'], count_from_schedule=True)

        last_backup = await backup.get(only_last_for_schedule=True, json_response=False)
        last_schedule_backup_stats = self._resources_stats(last_backup['items'])

        restores = await restore.get(json_response=False)
        all_restores_stats = self._resources_stats(restores['items'])

        schedules = await schedule.get(json_response=False)
        schedules_stats = self._schedules_stats(schedules['items'])

        last_backup_sorted = sorted(backups['items'], key=self.get_completion_timestamp, reverse=True)[:5]

        scheduled_namespace = self._get_all_scheduled_namespace(schedules['items'])
        all_ns = await k8s.get_ns()
        unscheduled_ns = list(set(all_ns) - set(scheduled_namespace))

        res = {'payload': {
            'backups': {
                'stats': {
                    'all': all_backups_stats,
                    'latest': last_schedule_backup_stats
                },
                'latest': last_backup_sorted,
            },
            'restores': {
                'all': all_restores_stats,
            },
            'schedules': {
              'all': schedules_stats
            },
            'namespaces': {
                'unscheduled': unscheduled_ns
            }
        }}

        return JSONResponse(content={'data': res}, status_code=201, headers={'X-Custom-Header': 'header-value'})

    @handle_exceptions_async_method
    async def in_progress(self):

        backups = await backup.get(in_progress=True, json_response=False, publish_message=False)

        restores = await restore.get(in_progress=True, json_response=False, publish_message=False)

        res = [*backups['items'], *restores['items']]

        i = 0
        for item in res:
            item['id'] = i + 1
            i += 1

        res2 = {'data': res}
        return JSONResponse(content=res2, status_code=201, headers={'X-Custom-Header': 'header-value'})

    @handle_exceptions_instance_method
    def parse_version_output(self, output):
        # Initialize the result dictionary
        result = {'client': {}, 'server': {}, 'warning': None}

        # Find client information
        client_match = re.search(r'Client:\n\tVersion:\s+(?P<version>[\w.-]+)\n\tGit commit:\s+(?P<git_commit>\w+)',
                                 output)
        if client_match:
            result['client']['version'] = client_match.group('version')
            result['client']['GitCommit'] = client_match.group('git_commit')

        # Finds server information
        server_match = re.search(r'Server:\n\tVersion:\s+(?P<version>[\w.-]+)', output)
        if server_match:
            result['server']['version'] = server_match.group('version')

        # Finds warning, if any
        warning_match = re.search(r'# WARNING:\s+(?P<warning>.+)', output)
        if warning_match:
            result['warning'] = warning_match.group('warning')

        return result

    @handle_exceptions_async_method
    async def version(self):
        output = await run_process_check_output(['velero', 'version'])

        if 'error' in output:
            return output

        res = {'payload': self.parse_version_output(output['data'])}

        return JSONResponse(content={'data': res}, status_code=201, headers={'X-Custom-Header': 'header-value'})

    @handle_exceptions_async_method
    async def get_env(self):
        env_data = config_app.get_env_variables()
        res = {'payload': env_data}

        return JSONResponse(content={'data': res}, status_code=201, headers={'X-Custom-Header': 'header-value'})

    @handle_exceptions_async_method
    async def get_origins(self):
        env_data = config_app.get_origins()
        res = {'payload': env_data}

        return JSONResponse(content={'data': env_data}, status_code=200)
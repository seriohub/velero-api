from core.config import ConfigHelper

from utils.handle_exceptions import handle_exceptions_async_method

from service.k8s_service import K8sService
from service.backup_service import BackupService
from service.restore_service import RestoreService
from service.schedule_service import ScheduleService

backup = BackupService()
restore = RestoreService()
schedule = ScheduleService()
k8sService = K8sService()
config_app = ConfigHelper()


class StatsService:

    def __resources_stats(self, resources, count_from_schedule=False):
        count = len(resources)

        completed = [x for x in resources if
                     'status' in x and 'phase' in x['status'] and x['status']['phase'] == 'Completed']
        completed_count = len(completed)

        partial_failed = [x for x in resources if
                          'status' in x and 'phase' in x['status'] and x['status']['phase'] == 'PartiallyFailed']
        partial_failed_count = len(partial_failed)

        failed = [x for x in resources if 'status' in x and 'phase' in x['status'] and x['status']['phase'] == 'Failed']
        failed_count = len(failed)

        scheduled = [x for x in resources if
                     'labels' in x['metadata'] and 'velero.io/schedule-name' in x['metadata']['labels']]
        scheduled_count = len(scheduled)

        res = {'count': count,
               # 'from_schedule_count': scheduled_count,
               'stats': [{'label': 'Completed',
                          'count': completed_count,
                          'perc': round(100 * completed_count / count if count > 0 else 0, 1),
                          'color': 'green'
                          },
                         {'label': 'Partial Failed',
                          'count': partial_failed_count,
                          'perc': round(100 * partial_failed_count / count if count > 0 else 0, 1),
                          'color': 'orange'
                          },
                         {'label': 'Failed',
                          'count': failed_count,
                          'perc': round(100 * failed_count / count if count > 0 else 0, 1),
                          'color': 'red'
                          }]
               }
        if count_from_schedule:
            res['from_schedule_count'] = scheduled_count
        return res

    def __schedules_stats(self, resources):
        count = len(resources)

        paused = [x for x in resources if 'paused' in x['spec']]

        paused_count = len(paused)

        unpaused_count = count - paused_count

        res = {'count': count,
               'from_schedule_count': 0,
               'stats': [
                   {'label': 'Unpaused',
                    'count': unpaused_count,
                    'perc': round(100 * unpaused_count / count if count > 0 else 0, 1),
                    'color': 'green'
                    },
                   {'label': 'Paused',
                    'count': paused_count,
                    'perc': round(100 * paused_count / count if count > 0 else 0, 1),
                    'color': 'red'
                    }]
               }
        return res

    def __get_all_scheduled_namespace(self, scheduled):
        unique_values_set = set()

        for item in scheduled:
            include_namespaces = item.get('spec', {}).get('template', {}).get('includedNamespaces', [])
            unique_values_set.update(include_namespaces)

        unique_values_list = list(unique_values_set)

        return unique_values_list

    def __get_completion_timestamp(self, item):
        return item['status'].get('completionTimestamp', str('-'))

    @handle_exceptions_async_method
    async def stats(self):

        backups = (await backup.get())['data']
        all_backups_stats = self.__resources_stats(backups, count_from_schedule=True)

        last_backup = (await backup.get(only_last_for_schedule=True))['data']
        last_schedule_backup_stats = self.__resources_stats(last_backup)

        restores = (await restore.get())['data']
        all_restores_stats = self.__resources_stats(restores)

        schedules = (await schedule.get())['data']
        schedules_stats = self.__schedules_stats(schedules)

        last_backup_sorted = sorted(backups, key=self.__get_completion_timestamp, reverse=True)[:5]

        scheduled_namespace = self.__get_all_scheduled_namespace(schedules)
        all_ns = (await k8sService.get_ns())['data']
        unscheduled_ns = list(set(all_ns) - set(scheduled_namespace))

        output = {
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
                'total': len(all_ns),
                'unscheduled': unscheduled_ns
            }
        }

        return {'success': True, 'data': output}

    @handle_exceptions_async_method
    async def in_progress(self):

        output = await backup.get(in_progress=True, publish_message=False)
        if not output['success']:
            return output

        backups = output['data']

        output = await restore.get(in_progress=True, publish_message=False)
        if not output['success']:
            return output

        restores = output['data']

        payload = [*backups, *restores]

        i = 0
        for item in payload:
            item['id'] = i + 1
            i += 1

        return {'success': True, 'data': payload}


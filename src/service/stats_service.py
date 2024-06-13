from core.config import ConfigHelper
from datetime import datetime, timedelta

import math
from croniter import croniter

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

    def __find_backup(self, backups, backup_name):
        return next((item for item in backups if item['metadata']['labels']['velero.io/schedule-name'] == backup_name), None)

    def __get_cron_events(self, cron_string, days=7):
        """
        Returns a list of events where the cron is triggered with hours, minutes and day of the week.

        :param cron_string: cron string (es. "24 00 * * 0" or "/30 * * * *")
        :param days:
        :return: List of dictionaries with 'hour', 'minute' and 'weekday'
        """
        start_time = datetime.now()
        end_time = start_time + timedelta(days=days)

        cron = croniter(cron_string, start_time)
        events = []

        while True:
            event_time = cron.get_next(datetime)
            if event_time > end_time:
                break
            # Convert weekday: 0 for Sunday, 1 for Monday, ..., 6 for Saturday
            weekday = (event_time.weekday() + 1) % 7
            new_event = {
                'start_hour': event_time.hour,
                'start_minute': event_time.minute,
                'weekday': weekday
            }
            events.append(new_event) if new_event not in events else events

        return events

    def __cron_heatmap_data(self, schedules, backups):
        data = []
        for sc in schedules:
            tmp = {'schedule_name': sc['metadata']['name'],
                   'cron': sc['spec']['schedule'],
                   'last': sc['status']['lastBackup'] if 'lastBackup' in sc['status'] and sc['status']['lastBackup'] else ''}

            last_backup = self.__find_backup(backups, tmp['schedule_name'])
            if tmp['last'] != '' and last_backup is not None and 'startTimestamp' in last_backup['status'] and 'completionTimestamp' in last_backup['status']:
                tmp['last_started'] = last_backup['status']['startTimestamp']
                tmp['last_finished'] = last_backup['status']['completionTimestamp']
                time1 = datetime.fromisoformat(tmp['last_started'].replace("Z", "+00:00"))
                time2 = datetime.fromisoformat(tmp['last_finished'].replace("Z", "+00:00"))
                time_difference = time2 - time1
                difference_in_minutes = time_difference.total_seconds() / 60
                tmp['duration'] = math.ceil(difference_in_minutes)
                events = self.__get_cron_events(tmp['cron'])
                for event in events:
                    event['duration'] = math.ceil(difference_in_minutes)
                    event['schedule_name'] = tmp['schedule_name']
                tmp['events'] = events
            data.append(tmp)
        return data

    def __create_event_matrix(self, events):
        # Create a 3D matrix of dimensions 7 days x 24 hours x 60 minutes, initially with zeros
        matrix = [[[0 for _ in range(60)] for _ in range(24)] for _ in range(7)]
        matrix_schedule_name = [[['' for _ in range(60)] for _ in range(24)] for _ in range(7)]

        for event in events:
            start_hour = event['start_hour']
            start_minute = event['start_minute']
            weekday = event['weekday']
            duration_minute = event['duration'] if 'duration' in event else 0

            # Calculates the total minutes since the beginning of the day
            start_time_in_minutes = start_hour * 60 + start_minute

            for minute in range(duration_minute):
                # Calculates the total time in minutes since the beginning of the week
                total_minutes = (weekday * 1440) + start_time_in_minutes + minute
                current_weekday = (total_minutes // 1440) % 7
                current_hour = (total_minutes % 1440) // 60
                current_minute = total_minutes % 60

                # Increases the counter in the array
                matrix[current_weekday][current_hour][current_minute] += 1
                matrix_schedule_name[current_weekday][current_hour][current_minute] += (',' if matrix_schedule_name[current_weekday][current_hour][current_minute] else '') + event['schedule_name']

        return matrix, matrix_schedule_name

    @handle_exceptions_async_method
    async def schedules(self):

        schedules = (await schedule.get())['data']
        backups = (await backup.get(only_last_for_schedule=True))['data']
        next_schedule = self.__cron_heatmap_data(schedules, backups)

        events = []

        for cron in next_schedule:
            if 'events' in cron:
                events = events + cron['events']

        matrix, matrix_schedule_name = self.__create_event_matrix(events)

        heatmap = {0: matrix[0],
                   1: matrix[1],
                   2: matrix[2],
                   3: matrix[3],
                   4: matrix[4],
                   5: matrix[5],
                   6: matrix[6]
                   }

        heatmap_schedule_name = {0: matrix_schedule_name[0],
                                 1: matrix_schedule_name[1],
                                 2: matrix_schedule_name[2],
                                 3: matrix_schedule_name[3],
                                 4: matrix_schedule_name[4],
                                 5: matrix_schedule_name[5],
                                 6: matrix_schedule_name[6]
                                 }

        # for day in range(7):
        #     print(f"Day {day}:")
        #     for hour in range(24):
        #         for minute in range(60):
        #             if matrix[day][hour][minute] > 0:
        #                 print(f"  {hour:02d}:{minute:02d} - {matrix[day][hour][minute]}")

        output = {
            'cron_heatmap': next_schedule,
            'week_heatmap': heatmap,
            'heatmap_schedule_name': heatmap_schedule_name
        }

        return {'success': True, 'data': output}

from configs.config_boot import config_app
from datetime import datetime, timedelta

import math
from croniter import croniter

from service.backup import get_backups_service
from service.restore import get_restores_service

from service.k8s import get_namespaces_service

from service.schedule import get_schedules_service


def _build_data(phase, counter, total_count):
    return {'label': phase,
            'count': counter,
            'perc': round(100 * counter / total_count if total_count > 0 else 0, 1),
            }


def _resources_stats(resources, count_from_schedule=False):
    count = len(resources)

    completed = [x for x in resources if
                 'status' in x and 'phase' in x['status'] and x['status']['phase'] == 'Completed']
    completed_count = len(completed)

    partial_failed = [x for x in resources if
                      'status' in x and 'phase' in x['status'] and x['status']['phase'] == 'PartiallyFailed']
    partial_failed_count = len(partial_failed)

    failed = [x for x in resources if 'status' in x and 'phase' in x['status'] and x['status']['phase'] == 'Failed']
    failed_count = len(failed)

    deleting = [x for x in resources if
                'status' in x and 'phase' in x['status'] and x['status']['phase'] == 'Deleting']
    deleting_count = len(deleting)

    failed_validation = [x for x in resources if
                         'status' in x and 'phase' in x['status'] and x['status']['phase'] == 'FailedValidation']
    failed_validation_count = len(failed_validation)

    scheduled = [x for x in resources if
                 'metadata' in x and
                 'labels' in x['metadata'] and
                 x['metadata']['labels'] is not None and
                 'velero.io/schedule-name' in x['metadata']['labels']]

    scheduled_count = len(scheduled)

    res = {'count': count,
           # 'from_schedule_count': scheduled_count,
           'stats': []}
    if completed_count > 0:
        #     res['stats'].append(
        #         {'label': 'Completed',
        #          'count': completed_count,
        #          'perc': round(100 * completed_count / count if count > 0 else 0, 1),
        #          }
        #     )
        res['stats'].append(
            _build_data(phase='Completed',
                        counter=completed_count,
                        total_count=count))
    if partial_failed_count > 0:
        # res['stats'].append(
        #     {'label': 'Partial Failed',
        #      'count': partial_failed_count,
        #      'perc': round(100 * partial_failed_count / count if count > 0 else 0, 1),
        #      })
        res['stats'].append(
            _build_data(phase='Partial Failed',
                        counter=partial_failed_count,
                        total_count=count))
    if failed_count > 0:
        # res['stats'].append(
        #     {'label': 'Failed',
        #      'count': failed_count,
        #      'perc': round(100 * failed_count / count if count > 0 else 0, 1),
        #      }
        # )
        res['stats'].append(
            _build_data(phase='Failed',
                        counter=failed_count,
                        total_count=count))
    if failed_validation_count > 0:
        # res['stats'].append(
        #     {'label': 'Failed Validation',
        #      'count': failed_validation_count,
        #      'perc': round(100 * failed_validation_count / count if count > 0 else 0, 1),
        #      }
        # )
        res['stats'].append(
            _build_data(phase='Failed Validation',
                        counter=failed_validation_count,
                        total_count=count))
    if deleting_count > 0:
        # res['stats'].append(
        #     {'label': 'Deleting',
        #      'count': deleting_count,
        #      'perc': round(100 * deleting_count / count if count > 0 else 0, 1),
        #      }
        # )
        res['stats'].append(
            _build_data(phase='Deleting',
                        counter=deleting_count,
                        total_count=count))

    if count_from_schedule:
        res['from_schedule_count'] = scheduled_count
    return res


def _schedules_stats(resources):
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


def _get_all_scheduled_namespace(scheduled):
    unique_values_set = set()

    for item in scheduled:
        include_namespaces = item.get('spec', {}).get('template', {}).get('includedNamespaces', [])
        unique_values_set.update(include_namespaces)

    unique_values_list = list(unique_values_set)

    return unique_values_list


def _get_completion_timestamp(item):
    return item['status']['completionTimestamp']


async def get_stats_service():
    backups = await get_backups_service()
    backups = [backup.model_dump() for backup in backups]

    all_backups_stats = _resources_stats(backups, count_from_schedule=True)

    last_backup = await get_backups_service(latest_per_schedule=True)
    last_backup = [backup.model_dump() for backup in last_backup]

    last_schedule_backup_stats = _resources_stats(last_backup)

    restores = await get_restores_service()
    restores = [restore.model_dump() for restore in restores]

    all_restores_stats = _resources_stats(restores)

    schedules = await get_schedules_service()
    schedules = [schedule.model_dump() for schedule in schedules]

    schedules_stats = _schedules_stats(schedules)

    last_backup_sorted = sorted(backups, key=_get_completion_timestamp, reverse=True)[:5]

    scheduled_namespace = _get_all_scheduled_namespace(schedules)
    all_ns = await get_namespaces_service()
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

    return output


async def get_in_progress_task_service():
    backups = await get_backups_service(in_progress=True)
    restores = await get_restores_service(in_progress=True)
    payload = [*backups, *restores]
    return payload


def _find_backup(backups, backup_name):
    return next(
        (item for item in backups if
         item.get('metadata', {}).get('labels', {}).get('velero.io/schedule-name') == backup_name),
        None
    )


def _get_cron_events(cron_string, days=7):
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


def _cron_heatmap_data(schedules, backups):
    data = []
    for sc in schedules:
        tmp = {'schedule_name': sc['metadata']['name'],
               'cron': sc['spec']['schedule'],
               'last': sc['status']['lastBackup'] if 'lastBackup' in sc['status'] and sc['status'][
                   'lastBackup'] else ''}

        last_backup = _find_backup(backups, tmp['schedule_name'])
        if tmp['last'] != '' and last_backup is not None and 'startTimestamp' in last_backup[
            'status'] and 'completionTimestamp' in last_backup['status']:
            tmp['last_started'] = last_backup['status']['startTimestamp']
            tmp['last_finished'] = last_backup['status']['completionTimestamp']
            time1 = datetime.fromisoformat(tmp['last_started'].replace("Z", "+00:00"))
            time2 = datetime.fromisoformat(tmp['last_finished'].replace("Z", "+00:00"))
            time_difference = time2 - time1
            difference_in_minutes = time_difference.total_seconds() / 60
            tmp['duration'] = math.ceil(difference_in_minutes)
            events = _get_cron_events(tmp['cron'])
            for event in events:
                event['duration'] = math.ceil(difference_in_minutes)
                event['schedule_name'] = tmp['schedule_name']
            tmp['events'] = events
        data.append(tmp)
    return data


def _create_event_matrix(events):
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
            matrix_schedule_name[current_weekday][current_hour][current_minute] += (',' if matrix_schedule_name[
                current_weekday][current_hour][current_minute] else '') + event['schedule_name']

    return matrix, matrix_schedule_name


async def get_schedules_heatmap_service():
    schedules = await get_schedules_service()
    schedules = [schedule.model_dump(exclude_unset=True) for schedule in schedules]

    backups = await get_backups_service(latest_per_schedule=True)
    backups = [backup.model_dump(exclude_unset=True) for backup in backups]
    next_schedule = _cron_heatmap_data(schedules, backups)

    events = []

    for cron in next_schedule:
        if 'events' in cron:
            events = events + cron['events']

    matrix, matrix_schedule_name = _create_event_matrix(events)

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

    return output

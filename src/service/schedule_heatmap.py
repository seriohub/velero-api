import math
from datetime import datetime, timedelta

from croniter import croniter

from service.backup import get_backups_service
from service.schedule import get_schedules_service
from vui_common.utils.k8s_tracer import trace_k8s_async_method


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
    if cron_string == '':
        return []
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
        tmp = {
            'schedule_name': sc.get('metadata', {}).get('name', ''),
            'cron': sc.get('spec', {}).get('schedule', ''),
            'last': sc.get('status', {}).get('lastBackup', '')
        }

        last_backup = _find_backup(backups, tmp['schedule_name'])
        if (tmp['last'] and last_backup and
                last_backup.get('status', {}).get('startTimestamp') and
                last_backup.get('status', {}).get('completionTimestamp')):

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


@trace_k8s_async_method(description="Get schedules heatmap")
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

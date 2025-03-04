from models.k8s.backup import BackupPhase
from service.backup import get_backups_service
from service.restore import get_restores_service
from collections import Counter
from service.k8s import get_namespaces_service

from service.schedule import get_schedules_service
from utils.k8s_tracer import trace_k8s_async_method


def _build_data(phase, counter, total_count):
    return {'label': phase,
            'count': counter,
            'perc': round(100 * counter / total_count if total_count > 0 else 0, 1),
            }


def _resources_stats(resources, count_from_schedule=False):
    """Generate statistics on backup resources, excluding phases with a count of 0."""

    total_count = len(resources)

    # Count occurrences of each backup phase
    # phase_counts = Counter(
    #     x['status']['phase'] for x in resources
    #     if isinstance(x, dict) and 'status' in x and 'phase' in x['status']
    # )
    phase_counts = Counter(
        x['status']['phase'] for x in resources
        if isinstance(x, dict) and isinstance(x.get('status'), dict) and 'phase' in x['status']
    )

    # Count scheduled backups
    scheduled_count = sum(
        1 for x in resources
        if isinstance(x, dict) and
        'metadata' in x and 'labels' in x['metadata'] and
        isinstance(x['metadata']['labels'], dict) and
        'velero.io/schedule-name' in x['metadata']['labels']
    )

    # Prepare response dictionary
    res = {'count': total_count, 'stats': []}

    # Include only phases that have a count greater than 0
    for phase in BackupPhase:
        count = phase_counts.get(phase.value, 0)
        if count > 0:
            res['stats'].append(
                _build_data(
                    phase=phase.value,
                    counter=count,
                    total_count=total_count
                )
            )

    # Add scheduled backups count if requested
    if count_from_schedule:
        res['from_schedule_count'] = scheduled_count

    return res


def _schedules_stats(resources):
    count = len(resources)

    paused = [x for x in resources if x.get('spec').get('paused') is True]

    paused_count = len(paused)

    unpaused_count = count - paused_count

    res = {'count': count,
           'from_schedule_count': 0,
           'stats': [
               {'label': 'Unpaused',
                'count': unpaused_count,
                'perc': round(100 * unpaused_count / count if count > 0 else 0, 1),
                },
               {'label': 'Paused',
                'count': paused_count,
                'perc': round(100 * paused_count / count if count > 0 else 0, 1),
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
    if not isinstance(item, dict):
        return ''  # Ensure item is a dictionary

    status = item.get('status')
    if not isinstance(status, dict):  # Ensure status is a dictionary
        return ''

    if status.get('completionTimestamp'):
        return status.get('completionTimestamp')

    return ''


@trace_k8s_async_method(description="Get service stats")
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

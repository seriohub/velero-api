import re
from datetime import datetime
from helpers.handle_exceptions import *
from connection_manager import manager



@handle_exceptions_instance_method
def is_valid_name(name):
    regex = r"[a-z0-9]([-a-z0-9]*[a-z0-9])?(\.[a-z0-9]([-a-z0-9]*[a-z0-9])?)*"
    return re.fullmatch(regex, name) is not None


@handle_exceptions_instance_method
def filter_in_progress(data):
    result = []

    for item in data:
        has_completion_timestamp = False
        diff_in_seconds = None
        datetime_completion_timestamp = None
        if 'completionTimestamp' in item['status']:
            has_completion_timestamp = True
            datetime_completion_timestamp = datetime.strptime(item['status']['completionTimestamp'],
                                                              '%Y-%m-%dT%H:%M:%SZ')
            now = datetime.utcnow()
            diff_in_seconds = (now - datetime_completion_timestamp).total_seconds()

        if (('status' in item and 'phase' in item['status']
             and (item['status']['phase'][-3:] == 'ing'
                  or item['status']['phase'].lower() == 'inprogress'
                  or (has_completion_timestamp and diff_in_seconds < 180))) or
                ('status' in item and not item['status'])):
            if has_completion_timestamp:
                item['status']['completionTimestamp'] = datetime_completion_timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
            result.append(item)
    return result


@handle_exceptions_instance_method
def logs_string_to_list(input_string):
    """

    :param input_string: all logs as string
    :type input_string: str

    :return: logs
    :rtype: array of dict

    """

    pattern = re.compile(r"(\w+)=(?:'(.*?)'|([^ ]*))")
    input_lines = input_string.split('\n')

    result_list = []

    # Iterate through the rows and apply the pattern to each
    for line in input_lines:
        matches = pattern.findall(line)
        result_dict = {field[0]: field[1] if field[1] else field[2] for field in matches}
        result_list.append(result_dict)

    i = 0
    for item in result_list:
        item['id'] = i + 1
        i += 1

    return result_list


@handle_exceptions_instance_method
def parse_create_parameters(info):
    cmd = []

    if 'includedNamespaces' in info['values'] and len(info['values']['includedNamespaces']) > 0:
        cmd.append('--include-namespaces')
        cmd.append(','.join(info['values']['includedNamespaces']))

    if 'excludedNamespaces' in info['values'] and info['values']['excludedNamespaces'] and len(
            info['values']['excludedNamespaces']) > 0:
        cmd.append('--exclude-namespaces')
        cmd.append(','.join(info['values']['excludedNamespaces']))

    if 'includedResources' in info['values'] and len(info['values']['includedResources']) > 0:
        cmd.append('--include-resources')
        cmd.append(','.join(info['values']['includedResources']))

    if 'excludedResources' in info['values'] and len(info['values']['excludedResources']) > 0:
        cmd.append('--exclude-resources')
        cmd.append(','.join(info['values']['excludedResources']))

    if 'backupRetention' in info['values'] and len(info['values']['backupRetention']) > 0:
        cmd.append('--ttl')
        cmd.append(info['values']['backupRetention'])

    # true or false
    if 'snapshotVolumes' in info['values'] and bool(info['values']['snapshotVolumes']):
        if info['values']['snapshotVolumes']:
            cmd.append('--snapshot-volumes=true')
        if not info['values']['snapshotVolumes']:
            cmd.append('--snapshot-volumes=false')

    # true, false or nil
    if 'includeClusterResources' in info['values'] and info['values']['includeClusterResources'] == 'true':
        cmd.append('--include-cluster-resources=true')
    if info['values']['includeClusterResources'] == 'false':
        cmd.append('--include-cluster-resources=false')

    # true or false
    if 'defaultVolumesToFsBackup' in info['values'] and bool(info['values']['defaultVolumesToFsBackup']) and \
            info['values']['defaultVolumesToFsBackup']:
        cmd.append('--default-volumes-to-fs-backup')

    if 'backup' in info['values'] and 'selector' in info['values'] and len(info['values']['backupLabel']) > 0 and len(
            info['values']['selector']) > 0:
        cmd.append('--selector')
        cmd.append(info['values']['backupLabel'] + '=' + info['values']['selector'])

    if 'backupLocation' in info['values'] and len(info['values']['backupLocation']) > 0:
        cmd.append('--storage-location')
        cmd.append(info['values']['backupLocation'].lower())

    if 'snapshotLocation' in info['values'] and len(list(filter(None, info['values']['snapshotLocation']))) > 0:
        cmd.append('--volume-snapshot-locations')
        cmd.append(','.join(info['values']['snapshotLocation']))

    if 'schedule' in info['values'] and len(info['values']['schedule']) > 0:
        cmd.append('--schedule')
        cmd.append(info['values']['schedule'])

    return cmd


@handle_exceptions_instance_method
def add_id_to_list(my_list):
    i = 0
    for item in my_list:
        item['id'] = i + 1
        i += 1


def extract_path(log_string):
    # Define a regular expression pattern to match the path
    path_pattern = r'/mnt/data/[^ ]+\.tar\.gz'

    # Use re.search to find the first match in the string
    match = re.search(path_pattern, log_string)

    # Check if a match is found
    if match:
        # Return the matched path
        return match.group()
    else:
        # Return None if no match is found
        return None


def trace_k8s_async_method(description):
    def decorator(fn):
        @wraps(fn)
        async def wrapper(*args, **kw):
            message = f"k8s {description}"
            print(message)
            await manager.broadcast(message)
            return await fn(*args, **kw)

        return wrapper

    return decorator


def route_description(tag='',
                      route='',
                      limiter_calls=0,
                      limiter_seconds=0):
    remove_char = ["/", "_", "-", "{", "}"]
    route_des = route[1:]
    for myChar in remove_char:
        route_des = route_des.replace(myChar, "_")

    key = f"{tag}:{route_des}"

    description = (f"Rate limiter key: {key} <br>Setup"
                   f": "
                   f"max {limiter_calls} calls for {limiter_seconds} seconds ")
    return description

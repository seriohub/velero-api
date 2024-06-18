import re
from datetime import datetime

def is_valid_name(name):
    regex = r"[a-z0-9]([-a-z0-9]*[a-z0-9])?(\.[a-z0-9]([-a-z0-9]*[a-z0-9])?)*"
    return re.fullmatch(regex, name) is not None


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


def parse_create_parameters(info):

    cmd = []

    if len(info.includedNamespaces) > 0:
        cmd.append('--include-namespaces')
        cmd.append(','.join(info.includedNamespaces))

    if info.excludedNamespaces and len(
            info.excludeNamespaces) > 0:
        cmd.append('--exclude-namespaces')
        cmd.append(','.join(info.excludedNamespaces))

    if len(info.includedResources) > 0:
        cmd.append('--include-resources')
        cmd.append(','.join(info.includedResources))

    if len(info.excludedResources) > 0:
        cmd.append('--exclude-resources')
        cmd.append(','.join(info.excludedResources))

    if len(info.backupRetention) > 0:
        cmd.append('--ttl')
        cmd.append(info.backupRetention)

    # true or false
    if bool(info.snapshotVolumes):
        if info.snapshotVolumes:
            cmd.append('--snapshot-volumes=true')
        if not info.snapshotVolumes:
            cmd.append('--snapshot-volumes=false')

    # true, false or nil
    if info.includeClusterResources == 'true':
        cmd.append('--include-cluster-resources=true')
    if info.includeClusterResources == 'false':
        cmd.append('--include-cluster-resources=false')

    # true or false
    if bool(info.defaultVolumesToFsBackup) and \
            info.defaultVolumesToFsBackup:
        cmd.append('--default-volumes-to-fs-backup')

    if len(info.backupLabel) > 0 and len(info.selector) > 0:
        cmd.append('--selector')
        cmd.append(info.backupLabel + '=' + info.selector)

    if len(info.backupLocation) > 0:
        cmd.append('--storage-location')
        cmd.append(info.backupLocation)

    if len(list(filter(None, info.snapshotLocation))) > 0:
        cmd.append('--volume-snapshot-locations')
        cmd.append(','.join(info.snapshotLocation))

    if hasattr(info, 'schedule') and len(info.schedule) > 0:
        cmd.append('--schedule')
        cmd.append(info.schedule)

    return cmd


def add_id_to_list(my_list):
    i = 0
    for item in my_list:
        item['id'] = i + 1
        i += 1


def extract_path(log_string):
    # Define a regular expression pattern to match the path
    path_pattern = r'/[^ ]+\.tar\.gz'

    # Use re.search to find the first match in the string
    match = re.search(path_pattern, log_string)

    # Check if a match is found
    if match:
        # Return the matched path
        return match.group()
    else:
        # Return None if no match is found
        return None


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


def convert_to_list(data):
    if not data['kind'].endswith('List'):
        return {'kind': data['kind'] + 'List', 'items': [data]}
    return data

import re


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

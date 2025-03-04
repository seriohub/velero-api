import re

import requests
from fastapi import HTTPException

from configs.config_boot import config_app
from utils.logger_boot import logger


def _get_compatibility(data, ui_version, api_version) -> bool:
    logger.info(f"__get_compatibility")
    is_ok = False

    logger.info(f"__get_compatibility.ui={ui_version}-api={api_version}")
    if len(api_version) > 0 and data:
        for revision in data:
            logger.info(f"__get_compatibility.json={revision}")
            is_ok = revision['api'] == api_version and revision['ui'] == ui_version
            if is_ok:
                break
    return is_ok


def _version_content(content, ui_version, api_version):
    logger.info(f"__version_content")
    lines = content.split('\n')
    header_index = None
    headers = []
    header_ui = -1
    header_api = -1
    i = 0
    for row, line in enumerate(lines):
        i += 1
        logger.debug(f'__version_content.line: {line}')
        idx_start = line.find('| version')
        if '| version' in line:
            logger.debug(f"__version_content.header found:{idx_start}")
            header_index = i
            header_line = line.strip()
            headers = header_line.split('|')[1:-1]
            headers = [h.strip() for h in headers]
            if ui_version:
                header_ui = headers.index("ui")
            if api_version:
                header_api = headers.index("api")
            break

    if header_index is None:
        message = "Header (| version ) row not found."
        logger.debug(message)
        return None, None, message
    # Process the data lines
    data_lines = lines[header_index + 1:]  # Skip the separator line
    versions_ui = []
    versions_api = []

    for line in data_lines:
        # logger.debug(f"stripped:{line}")
        if line and line.strip():
            data = line.strip().split('|')[1:-1]
            data = [d.strip() for d in data]
            add_row = True
            if ui_version:
                # logger.debug(f"header:{data[header_ui] }- required:{ui_version}")
                add_row = data[header_ui] == ui_version

            if add_row:
                version_info = {headers[i]: data[i] for i in range(len(headers))}
                versions_ui.append(version_info)

            add_row = True
            if api_version:
                add_row = data[header_api] == api_version
            if add_row:
                version_info = {headers[i]: data[i] for i in range(len(headers))}
                versions_api.append(version_info)
        else:
            break

    logger.debug(f"__retrieve_data_from_md_file output data: {versions_ui}")

    return versions_ui, versions_api, None


def _retrieve_data_from_md_file(ui_version: str = None, api_version: str = None):
    logger.info(f"__retrieve_data_from_md_file")
    url = 'https://raw.githubusercontent.com/seriohub/velero-helm/main/components.txt'
    response = requests.get(url)

    if response.status_code == 200:
        content = response.text
        versions_ui, versions_api, msg_error = _version_content(content, ui_version, api_version)
        return versions_ui, versions_api, msg_error
    else:
        message = "no data read from md file"
        logger.info(f"__retrieve_data_from_md_file: {message}")
        return None, None, message


async def ui_compatibility_service(version: str):
    logger.info(f"ui_compatibility version: {version}")

    # avoid error in developer mode
    if version == "dev" or version == "local dev":
        output = {'compatibility': True}
        return output

    if version and len(version) > 0:
        # Compile the regex pattern
        version_regex = re.compile(r'^(dev|\d+\.\d+\.\d+)$')
        if version_regex.match(version):
            output = {}
            # is_comp = False
            api_version = config_app.app.build_version
            # retrieve data from github
            data_ui, data_api, error = _retrieve_data_from_md_file(ui_version=version,
                                                                   api_version=api_version)
            if data_ui is None:
                raise HTTPException(status_code=400,
                                    detail=f"Error get data from GitHub repository', 'description': {error}")

            is_comp = _get_compatibility(data=data_ui, ui_version=version, api_version=api_version)

            output['compatibility'] = is_comp
            output['versions_ui'] = data_ui
            output['versions_api'] = data_api
            return output
        else:
            raise HTTPException(status_code=400, detail=f'Parameters missed')

    else:
        raise HTTPException(status_code=400, detail=f'Parameters missed, No version provided')

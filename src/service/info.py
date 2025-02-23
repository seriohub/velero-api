import platform

import aiohttp
import requests
import starlette.status
from fastapi import HTTPException

from configs.config_boot import config_app

from datetime import datetime
import re

from models.db.project_versions import ProjectsVersion
from database.db_connection import SessionLocal
from typing import Optional

from utils.logger_boot import logger

last_version_data = {}
last_version_scan_datetime = datetime.utcnow()


def _extract_version_numbers(tag_name):
    # Use regular expression to extract integers from the tag name
    numbers = re.findall(r'\d+', tag_name)
    # Convert extracted numbers into integers and return as a tuple
    return tuple(map(int, numbers))


def _prepare_json_out(api, ui, helm, watchdog, velero, timestamp) -> dict:
    logger.info(f"__prepare_json_out")
    output = {'api': '' if api is None else api, 'ui': '' if ui is None else ui,
              'helm': '' if helm is None else helm, 'watchdog': '' if watchdog is None else watchdog,
              'velero': '' if velero is None else velero, 'datetime': timestamp.strftime("%d/%m/%Y %H:%M:%S")}
    return output


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


def _get_last_version_from_db(db: SessionLocal) -> Optional[ProjectsVersion]:
    logger.info(f"__get_last_data_from_db")
    data = db.query(ProjectsVersion).first()
    if data:
        return data
    return None


def _save_last_version_from_db(api, ui, helm, watchdog, velero, db: SessionLocal):
    logger.info(f"__save_last_version_from_db")
    old_data = db.query(ProjectsVersion).first()
    if old_data:
        db.delete(old_data)
    # LS 2024.12.12 add velero version
    new_data = ProjectsVersion(time_created=datetime.utcnow(), pv_1=api, pv_2=ui, pv_3=helm, pv_4=watchdog,
                               pv_5=velero)

    db.add(new_data)
    db.commit()
    return None


async def _is_elapsed_time_to_scrapy():
    diff = datetime.utcnow() - last_version_scan_datetime
    logger.info(f"minutes elapsed {round(diff.total_seconds() / 60, 2)} - "
                f"threshold {config_app.get_github_scrapy_versions_minutes()}")
    return (diff.total_seconds() / 60) > config_app.get_github_scrapy_versions_minutes()


async def _do_api_call(url):
    logger.debug(f'__do_api_call URL {url}')
    timeout = aiohttp.ClientTimeout(total=10)  # Increase total timeout to 10 seconds
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as response:
                output = await response.json()
                return {'status': response.status, 'data': output}

    except aiohttp.ClientError as e:
        logger.error(f"[{url}] Error during async request: {e}")
        return {'status': starlette.status.HTTP_404_NOT_FOUND, 'data': None}


async def _get_last_version(repo, owner="seriohub", check_last_release=False) -> str:
    # LS 2024.12.12 moved to parameter
    # owner = "seriohub"
    # GitHub API URL for fetching all tags
    path = "tags"
    if check_last_release:
        path = "releases/latest"
    url = f"https://api.github.com/repos/{owner}/{repo}/{path}"

    # Make the request
    # response = requests.get(url)
    response = await _do_api_call(url)
    if response['status'] == 200:
        try:
            # data = await response.json()
            data = response['data']
            if check_last_release:
                latest_tag = f"{data.get('tag_name')} published at {data.get('published_at')}"
            else:
                tags = data
                tags.sort(key=lambda tag: _extract_version_numbers(tag["name"]), reverse=True)
                latest_tag = tags[0]["name"]

            logger.info(f"The latest tag for the repo {repo} is: {latest_tag}")
            return latest_tag
        except Exception as e:
            logger.error(f"Error processing response for {repo}: {e}")
            return "n.y.a."
    else:
        logger.warning(f"Failed to fetch tags for repo {repo}. Status code: {str(response)}")
        return "n.y.a."


async def identify_architecture_service():
    architecture = platform.machine()

    identify = False
    if architecture == 'AMD64' or architecture == 'x86_64':
        identify = True
        arch = 'amd64'
    elif architecture.startswith('arm'):
        identify = True
        arch = 'arm'
    elif architecture.startswith('aarch64'):
        identify = True
        arch = 'arm64'
    else:
        arch = 'Error: Unsupported architecture'

    output = {'arch': arch, }
    if not identify:
        output['platform'] = platform.machine()

    return output


async def last_tags_from_github_service(db: SessionLocal, check_version=True, only_velero=False, force_refresh=False):
    global last_version_data
    global last_version_scan_datetime
    in_memory = False
    data_is_empty = True
    # Check in memory
    if not force_refresh:
        if len(last_version_data) > 0:
            data_is_empty = False
            in_memory = not (await _is_elapsed_time_to_scrapy())
        # Check in db
        if not in_memory:
            logger.info(f"Find in db")
            # get data from db
            data = _get_last_version_from_db(db)
            if data is not None:
                data_is_empty = False
                last_version_data = _prepare_json_out(data.pv_1, data.pv_2, data.pv_3, data.pv_4,
                                                      data.pv_5, data.time_created)
                last_version_scan_datetime = data.time_created
        # Verify the data
        if not in_memory:
            if len(last_version_data) > 0:
                data_is_empty = False
                in_memory = not (await _is_elapsed_time_to_scrapy())

        logger.info(f"Dict {'is empty' if data_is_empty else 'is not empty'} and use memory {in_memory}")
    else:
        logger.info(f"Force scrapy data")

    if in_memory:
        logger.info(f"get in-memory data (no scrapy is done). "
                    f"last scan: {last_version_scan_datetime.strftime('%d/%m/%Y %H:%M:%S')}"
                    f"- cycle time min {config_app.get_github_scrapy_versions_minutes()}")
        output = last_version_data
    else:
        logger.info(f"scrapy the last version from github")
        api = await _get_last_version(repo="velero-api")
        helm = await _get_last_version(repo="velero-helm")
        watchdog = await _get_last_version(repo="velero-watchdog")
        ui = await _get_last_version(repo="velero-ui")

        # LS 2024.12.12 add last version of velero
        velero = await _get_last_version(repo="velero", owner="vmware-tanzu",
                                         check_last_release=check_version)

        output = _prepare_json_out(api, ui, helm, watchdog, velero, datetime.utcnow())

        last_version_data = output
        last_version_scan_datetime = datetime.utcnow()
        _save_last_version_from_db(api, ui, helm, watchdog, velero, db)

    # LS 2024.12.12 filter the velero tag if required
    if only_velero:
        output_data = {'velero': output["velero"], "datetime": output["datetime"]}
    else:
        output_data = output.copy()
        del output_data["velero"]

    return output_data


async def ui_compatibility_service(version: str):
    logger.info(f"ui_compatibility version :{version}")

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
            api_version = config_app.get_build_version()
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

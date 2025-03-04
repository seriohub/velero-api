import aiohttp
import starlette.status

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
                f"threshold {config_app.app.scrapy_version}")
    return (diff.total_seconds() / 60) > config_app.app.scrapy_version


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
                    f"- cycle time min {config_app.app.scrapy_version}")
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



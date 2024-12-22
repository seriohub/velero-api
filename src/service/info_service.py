import base64
import platform

import aiohttp
import requests
import starlette.status

from core.config import ConfigHelper
from helpers.printer import PrintHelper
from utils.handle_exceptions import handle_exceptions_async_method
from datetime import datetime, timedelta
import re

from security.helpers.database import ProjectsVersion
from security.helpers.database import SessionLocal
from typing import Optional


def extract_version_numbers(tag_name):
    # Use regular expression to extract integers from the tag name
    numbers = re.findall(r'\d+', tag_name)
    # Convert extracted numbers into integers and return as a tuple
    return tuple(map(int, numbers))


class InfoService:
    def __init__(self):
        self.config_app = ConfigHelper()
        self.print_ls = PrintHelper(['service.info'],
                                    level=self.config_app.get_internal_log_level())

        self.last_version_data = {}
        self.last_version_scan_datetime = datetime.utcnow()

    def __prepare_json_out(self, api, ui, helm, watchdog, velero, timestamp):
        self.print_ls.info(f"__prepare_json_out")
        output = {
            'api': '' if api is None else api,
            'ui': '' if ui is None else ui,
            'helm': '' if helm is None else helm,
            'watchdog': '' if watchdog is None else watchdog,
            'velero': '' if velero is None else velero,
            'datetime': timestamp.strftime("%d/%m/%Y %H:%M:%S")
        }
        return output

    def __get_compatibility(self, data, ui_version, api_version):
        self.print_ls.info(f"__get_compatibility")
        is_ok = False

        self.print_ls.info(f"__get_compatibility.ui={ui_version}-api={api_version}")
        if len(api_version) > 0 and data:
            for revision in data:
                self.print_ls.info(f"__get_compatibility.json={revision}")
                is_ok = revision['api'] == api_version and revision['ui'] == ui_version
                if is_ok:
                    break
        return is_ok

    def __version_content(self, content, ui_version, api_version):
        self.print_ls.info(f"__version_content")
        lines = content.split('\n')
        header_index = None
        headers = []
        header_ui = -1
        header_api = -1
        i = 0
        for row, line in enumerate(lines):
            i += 1
            self.print_ls.debug(f'__version_content.line: {line}')
            idx_start = line.find('| version')
            if '| version' in line:
                self.print_ls.debug(f"__version_content.header found:{idx_start}")
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
            self.print_ls.debug(message)
            return None, None, message
        # Process the data lines
        data_lines = lines[header_index + 1:]  # Skip the separator line
        versions_ui = []
        versions_api = []

        for line in data_lines:
            # self.print_ls.debug(f"stripped:{line}")
            if line and line.strip():
                data = line.strip().split('|')[1:-1]
                data = [d.strip() for d in data]
                add_row = True
                if ui_version:
                    # self.print_ls.debug(f"header:{data[header_ui] }- required:{ui_version}")
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

        self.print_ls.trace(f"__retrieve_data_from_md_file output data: {versions_ui}")

        return versions_ui, versions_api, None

    def __retrieve_data_from_md_file(self, ui_version: str = None, api_version: str = None):
        self.print_ls.info(f"__retrieve_data_from_md_file")
        url = 'https://raw.githubusercontent.com/seriohub/velero-helm/main/components.txt'
        response = requests.get(url)

        if response.status_code == 200:
            content = response.text
            versions_ui, versions_api, msg_error = self.__version_content(content,
                                                                          ui_version,
                                                                          api_version)
            return versions_ui, versions_api, msg_error
        else:
            message = "no data read from md file"
            self.print_ls.info(f"__retrieve_data_from_md_file: {message}")
            return None, None, message

    def __get_last_version_from_db(self, db: SessionLocal) -> Optional[ProjectsVersion]:
        self.print_ls.info(f"__get_last_data_from_db")
        data = db.query(ProjectsVersion).first()
        if data:
            return data
        return None

    def __save_last_version_from_db(self, api, ui, helm, watchdog, velero, db: SessionLocal):
        self.print_ls.info(f"__save_last_version_from_db")
        old_data = db.query(ProjectsVersion).first()
        if old_data:
            db.delete(old_data)
        # LS 2024.12.12 add velero version
        new_data = ProjectsVersion(time_created=datetime.utcnow(),
                                   pv_1=api,
                                   pv_2=ui,
                                   pv_3=helm,
                                   pv_4=watchdog,
                                   pv_5=velero)

        db.add(new_data)
        db.commit()
        return None

    async def __is_elapsed_time_to_scrapy(self):
        diff = datetime.utcnow() - self.last_version_scan_datetime
        self.print_ls.info(f"minutes elapsed {round(diff.total_seconds() / 60, 2)} - "
                           f"threshold {self.config_app.get_github_scrapy_versions_minutes()}")
        return (diff.total_seconds() / 60) > self.config_app.get_github_scrapy_versions_minutes()

    async def __do_api_call(self, url):
        self.print_ls.debug(f'__do_api_call URL {url}')
        timeout = aiohttp.ClientTimeout(total=10)  # Increase total timeout to 10 seconds
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    output = await response.json()
                    return {'status': response.status, 'data': output}

        except aiohttp.ClientError as e:
            self.print_ls.error(f"[{url}] Error during async request: {e}")
            return {'status': starlette.status.HTTP_404_NOT_FOUND  , 'data': None}

    async def __get_last_version(self, repo, owner="seriohub", check_last_release=False) -> str:
        # LS 2024.12.12 moved to parameter
        #owner = "seriohub"
        # GitHub API URL for fetching all tags
        path = "tags"
        if check_last_release:
            path = "releases/latest"
        url = f"https://api.github.com/repos/{owner}/{repo}/{path}"

        # Make the request
        # response = requests.get(url)
        response = await self.__do_api_call(url)
        if response['status'] == 200:
            try:
                # data = await response.json()
                data = response['data']
                if check_last_release:
                    latest_tag = f"{data.get('tag_name')} published at {data.get('published_at')}"
                else:
                    tags = data
                    tags.sort(key=lambda tag: extract_version_numbers(tag["name"]), reverse=True)
                    latest_tag = tags[0]["name"]

                self.print_ls.info(f"The latest tag for the repo {repo} is: {latest_tag}")
                return latest_tag
            except Exception as e:
                self.print_ls.error(f"Error processing response for {repo}: {e}")
                return "-"
        else:
            self.print_ls.wrn(f"Failed to fetch tags for repo {repo}. Status code: {response.status}")
            return "-"

    @handle_exceptions_async_method
    async def identify_architecture(self):
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

        output = {
            'arch': arch,
        }
        if not identify:
            output['platform'] = platform.machine()

        return {'success': True, 'data': output}

    @handle_exceptions_async_method
    async def last_tags_from_github(self, db: SessionLocal, check_version=True, only_velero=False, force_refresh=False):
        in_memory = False
        data_is_empty = True
        # Check in memory
        if not force_refresh:
            if len(self.last_version_data) > 0:
                data_is_empty = False
                in_memory = not (await self.__is_elapsed_time_to_scrapy())
            # Check in db
            if not in_memory:
                self.print_ls.info(f"Find in db")
                # get data from db
                data = self.__get_last_version_from_db(db)
                if data is not None:
                    data_is_empty = False
                    self.last_version_data = self.__prepare_json_out(data.pv_1,
                                                                     data.pv_2,
                                                                     data.pv_3,
                                                                     data.pv_4,
                                                                     data.pv_5,
                                                                     data.time_created)
                    self.last_version_scan_datetime = data.time_created
            # Verify the data
            if not in_memory:
                if len(self.last_version_data) > 0:
                    data_is_empty = False
                    in_memory = not (await self.__is_elapsed_time_to_scrapy())

            self.print_ls.info(f"Dict {'is empty' if data_is_empty else 'is not empty'} and use memory {in_memory}")
        else:
            self.print_ls.info(f"Force scrapy data")

        if in_memory:
            self.print_ls.info(f"get in-memory data (no scrapy is done). "
                               f"last scan: {self.last_version_scan_datetime.strftime('%d/%m/%Y %H:%M:%S')}"
                               f"- cycle time min {self.config_app.get_github_scrapy_versions_minutes()}")
            output = self.last_version_data
        else:
            self.print_ls.info(f"scrapy the last version from github")
            api = await self.__get_last_version(repo="velero-api")
            helm = await self.__get_last_version(repo="velero-helm")
            watchdog = await self.__get_last_version(repo="velero-watchdog")
            ui = await self.__get_last_version(repo="velero-ui")

            # LS 2024.12.12 add last version of velero
            velero = await self.__get_last_version(repo="velero",
                                                   owner="vmware-tanzu",
                                                   check_last_release=check_version)

            output = self.__prepare_json_out(api,
                                             ui,
                                             helm,
                                             watchdog,
                                             velero,
                                             datetime.utcnow())

            self.last_version_data = output
            self.last_version_scan_datetime = datetime.utcnow()
            self.__save_last_version_from_db(api,
                                             ui,
                                             helm,
                                             watchdog,
                                             velero,
                                             db)

        # LS 2024.12.12 filter the velero tag if required
        if only_velero:
            output_data = {'velero': output["velero"],
                           "datetime": output["datetime"]}
        else:
            output_data = output.copy()
            del output_data["velero"]

        return {'success': True, 'data': output_data}

    @handle_exceptions_async_method
    async def ui_compatibility(self, version: str):
        self.print_ls.info(f"ui_compatibility version :{version}")

        # avoid error in developer mode
        if version == "dev":
            output = {'compatibility': True}
            return {'success': True, 'data': output}

        if version and len(version) > 0:
            # Compile the regex pattern
            version_regex = re.compile(r'^(dev|\d+\.\d+\.\d+)$')
            if version_regex.match(version):
                output = {}
                is_comp = False
                api_version = self.config_app.get_build_version()
                # retrieve data from github
                data_ui, data_api, error = self.__retrieve_data_from_md_file(ui_version=version,
                                                                             api_version=api_version)
                if data_ui is None:
                    return {'success': False, 'error': {'title': 'Error get data from GitHub repository',
                                                        'description': error
                                                        }
                            }
                is_comp = self.__get_compatibility(data=data_ui,
                                                   ui_version=version,
                                                   api_version=api_version)

                output['compatibility'] = is_comp
                output['versions_ui'] = data_ui
                output['versions_api'] = data_api
                return {'success': True, 'data': output}
            else:
                return {'success': False, 'error': {'title': 'Parameters missed',
                                                    'description': f'The ui version provided {version} '
                                                                   f'is not a valid version'
                                                    }}
        else:
            return {'success': False, 'error': {'title': 'Parameters missed',
                                                'description': 'No version provided'
                                                }}

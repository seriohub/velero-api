import platform
import requests
from core.config import ConfigHelper
from helpers.printer import PrintHelper
from utils.handle_exceptions import handle_exceptions_async_method
from datetime import datetime, timedelta

from security.helpers.database import ProjectsVersion
from security.helpers.database import SessionLocal
from typing import Optional


class InfoService:
    def __init__(self):
        self.config_app = ConfigHelper()
        self.print_ls = PrintHelper(['service.info'],
                                    level=self.config_app.get_internal_log_level())

        self.last_version_data = {}
        self.last_version_scan_datetime = datetime.utcnow()

    def __prepare_json_out(self, api, ui, helm, watchdog, timestamp):
        self.print_ls.info(f"__prepare_json_out")
        output = {
            'api': '' if api is None else api,
            'ui': '' if ui is None else ui,
            'helm': '' if helm is None else helm,
            'watchdog': '' if watchdog is None else watchdog,
            'datetime': timestamp.strftime("%d/%m/%Y %H:%M:%S")
        }
        return output

    def __get_last_version_from_db(self, db: SessionLocal) -> Optional[ProjectsVersion]:
        self.print_ls.info(f"__get_last_data_from_db")
        data = db.query(ProjectsVersion).first()
        if data:
            return data
        return None

    def __save_last_version_from_db(self, api, ui, helm, watchdog, db: SessionLocal):
        self.print_ls.info(f"__save_last_version_from_db")
        old_data = db.query(ProjectsVersion).first()
        if old_data:
            db.delete(old_data)
        new_data = ProjectsVersion(time_created=datetime.utcnow(),
                                   pv_1=api,
                                   pv_2=ui,
                                   pv_3=helm,
                                   pv_4=watchdog)

        db.add(new_data)
        db.commit()
        return None

    async def __is_elapsed_time_to_scrapy(self):
        diff = datetime.utcnow() - self.last_version_scan_datetime
        self.print_ls.info(f"minutes elapsed {round(diff.total_seconds() / 60, 2)} - "
                           f"threshold {self.config_app.get_github_scrapy_versions_minutes()}")
        return (diff.total_seconds() / 60) > self.config_app.get_github_scrapy_versions_minutes()

    async def __get_last_version(self, repo):
        owner = "seriohub"
        # GitHub API URL for fetching all tags
        url = f"https://api.github.com/repos/{owner}/{repo}/tags"

        # Make the request
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            # Extract the tags from the response
            tags = response.json()

            # Sort the tags based on the tag name (assuming semantic versioning)
            tags.sort(key=lambda tag: tag['name'], reverse=True)

            # The first tag in the sorted list is the latest
            latest_tag = tags[0]['name']
            self.print_ls.info(f"The latest tag for the repo {repo} is: {latest_tag}")
            return latest_tag
        else:
            self.print_ls.wrn(f"Failed to fetch the tags for the repo {repo}. Status code: {response.status_code}")
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
    async def last_tags_from_github(self, db: SessionLocal):
        in_memory = False
        data_is_empty = True
        # Check in memory
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
                                                                 data.time_created)
                self.last_version_scan_datetime = data.time_created
        # Verify the data
        if not in_memory:
            if len(self.last_version_data) > 0:
                data_is_empty = False
                in_memory = not (await self.__is_elapsed_time_to_scrapy())

        self.print_ls.info(f"Dict {'is empty' if data_is_empty else 'is not empty'} and use memory {in_memory}")

        if in_memory:
            self.print_ls.info(f"get in-memory data (no scrapy is done). "
                               f"last scan: {self.last_version_scan_datetime.strftime('%d/%m/%Y %H:%M:%S')}"
                               f"- cycle time min {self.config_app.get_github_scrapy_versions_minutes()}")
            output = self.last_version_data
        else:
            self.print_ls.info(f"scrapy the last version from github")
            api = await self.__get_last_version("velero-api")
            helm = await self.__get_last_version("velero-helm")
            watchdog = await self.__get_last_version("velero-watchdog")
            ui = await self.__get_last_version("velero-ui")

            output = self.__prepare_json_out(api, ui, helm, watchdog, datetime.utcnow())

            self.last_version_data = output
            self.last_version_scan_datetime = datetime.utcnow()
            self.__save_last_version_from_db(api, ui, helm, watchdog, db)

        return {'success': True, 'data': output}

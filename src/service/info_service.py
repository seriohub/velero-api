import platform
import requests
from core.config import ConfigHelper
from helpers.printer import PrintHelper
from utils.handle_exceptions import handle_exceptions_async_method


class InfoService:
    def __init__(self):
        self.config_app = ConfigHelper()
        self.print_ls = PrintHelper(['service.info'],
                                    level=self.config_app.get_internal_log_level())

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
    async def last_tags_from_github(self):
        api = await self.__get_last_version("velero-api")
        helm = await self.__get_last_version("velero-helm")
        watchdog = await self.__get_last_version("velero-watchdog")
        ui = await self.__get_last_version("velero-ui")
        output = {
            'api': api,
            'ui': ui,
            'helm': helm,
            'watchdog': watchdog,
        }

        return {'success': True, 'data': output}

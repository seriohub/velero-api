import os
import re

from utils.handle_exceptions import handle_exceptions_async_method
from utils.process import run_process_check_output


class SetupService:

    def __parse_version_output(self, output):
        # Initialize the result dictionary
        result = {'client': {}, 'server': {}, 'warning': None}

        # Find client information
        client_match = re.search(r'Client:\n\tVersion:\s+(?P<version>[\w.-]+)\n\tGit commit:\s+(?P<git_commit>\w+)',
                                 output)
        if client_match:
            result['client']['version'] = client_match.group('version')
            result['client']['GitCommit'] = client_match.group('git_commit')

        # Finds server information
        server_match = re.search(r'Server:\n\tVersion:\s+(?P<version>[\w.-]+)', output)
        if server_match:
            result['server']['version'] = server_match.group('version')

        # Finds warning, if any
        warning_match = re.search(r'# WARNING:\s+(?P<warning>.+)', output)
        if warning_match:
            result['warning'] = warning_match.group('warning')

        return result

    @handle_exceptions_async_method
    async def version(self):
        output = await run_process_check_output(['velero', 'version',
                                                 '-n', os.getenv('K8S_VELERO_NAMESPACE', 'velero')])

        if not output['success']:
            return output

        return {'success': True, 'data': self.__parse_version_output(output['data'])}

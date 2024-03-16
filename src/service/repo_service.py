import json
import os

from utils.commons import add_id_to_list
from utils.process import run_process_check_output
from utils.handle_exceptions import handle_exceptions_async_method


class RepoService:

    @handle_exceptions_async_method
    async def get(self):
        output = await run_process_check_output(['velero', 'repo', 'get', '-o', 'json',
                                                 '-n', os.getenv('K8S_VELERO_NAMESPACE', 'velero')])
        if not output['success']:
            return output

        repos = json.loads(output['data'])

        if repos['kind'].lower() == 'backuprepository':
            repos = {'items': [repos]}

        add_id_to_list(repos['items'])

        return {'success': True, 'data': repos['items']}

    @handle_exceptions_async_method
    async def get_locks(self, repository_url):
        output = await run_process_check_output(['restic', '-q', '--no-lock', 'list', 'locks', '-r', repository_url])

        if not output['success']:
            return output

        locks = output['data']

        return {'success': True, 'data':  {str(repository_url): list(filter(None, locks.split('\n')))}}

    @handle_exceptions_async_method
    async def unlock(self, repository_url, remove_all=False):
        cmd = ['restic', 'unlock', '-r', repository_url]
        if remove_all:
            cmd.append('--remove-all')

        output = await run_process_check_output(cmd)

        if not output['success']:
            return output

        locks = output['data']

        return {'success': True, 'data':  {str(repository_url): list(filter(None, locks.split('\n')))}}

    @handle_exceptions_async_method
    async def check(self, repository_url):
        cmd = ['restic', 'check', '-r', repository_url]

        output = await run_process_check_output(cmd)

        if not output['success']:
            return output

        check = output['data']

        return {'success': True, 'data':  {str(repository_url): list(filter(None, check.split('\n')))}}

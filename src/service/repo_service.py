import json
import os
import re

from core.config import ConfigHelper

# from utils.commons import add_id_to_list
from utils.minio_wrapper import MinioInterface
from utils.process import run_process_check_output
from utils.handle_exceptions import handle_exceptions_async_method

config = ConfigHelper()


class RepoService:

    @handle_exceptions_async_method
    async def get(self):
        output = await run_process_check_output(
            ['velero', 'repo', 'get', '-o', 'json', '-n', os.getenv('K8S_VELERO_NAMESPACE', 'velero')])
        if not output['success']:
            return output

        repos = json.loads(output['data'])

        if repos['kind'].lower() == 'backuprepository':
            repos = {'items': [repos]}

        # add_id_to_list(repos['items'])

        return {'success': True, 'data': repos['items']}

    @handle_exceptions_async_method
    async def get_backup_size(self, repository_url: str = None, backup_storage_location: str = None,
                              repository_name: str = None, repository_type: str = None, volume_namespace: str = None):

        minio_interface = MinioInterface()

        # temporary fix url
        if repository_type.lower() == 'kopia':
            repository_url = repository_url.replace('/restic/', '/kopia/')

        # endpoint match
        endpoint_match = re.search(r's3:(http://[^/]+)', repository_url)
        if endpoint_match:
            endpoint_with_protocol = endpoint_match.group(1)
            # remove protocol
            endpoint = re.sub(r'https?://', '', endpoint_with_protocol)
            print("Endpoint:", endpoint)
        else:
            endpoint = 'default'
            # TODO raise error
            print("No endpoint found.")

        # extract bucket name
        match = re.search(r's3:http://[^/]+/([^/]+)/', repository_url)
        if match:
            bucket_name = match.group(1)
            print(bucket_name)
        else:
            bucket_name = 'default'
            # TODO raise error
            print("No bucket name found.")

        return await minio_interface.get_backup_size(repository_url=repository_url, endpoint=endpoint,
                                                     backup_storage_location=backup_storage_location,
                                                     bucket_name=bucket_name, repository_name=repository_name,
                                                     repository_type=repository_type, volume_namespace=volume_namespace)

    @handle_exceptions_async_method
    async def get_locks(self, env, repository_url):

        cmd = ['restic', '-q', '--no-lock', 'list', 'locks', '-r', repository_url]

        output = await run_process_check_output(cmd=cmd, env=env)

        if not output['success']:
            return output

        locks = output['data']

        return {'success': True, 'data': {str(repository_url): list(filter(None, locks.split('\n')))}}

    @handle_exceptions_async_method
    async def unlock(self, env, bsl, repository_url, remove_all=False):
        cmd = ['restic', 'unlock', '-r', repository_url]
        if remove_all:
            cmd.append('--remove-all')

        output = await run_process_check_output(cmd=cmd, env=env)

        if not output['success']:
            return output

        locks = output['data']

        return {'success': True, 'data': {'bsl': bsl,
                                          'repositoryUrl': str(repository_url),
                                          'locks': list(filter(None, locks.split('\n')))}
                }

    @handle_exceptions_async_method
    async def check(self, env, repository_url):
        cmd = ['restic', 'check', '-r', repository_url]

        output = await run_process_check_output(cmd=cmd, env=env)

        if not output['success']:
            return output

        check = output['data']

        return {'success': True, 'data': {str(repository_url): list(filter(None, check.split('\n')))}}

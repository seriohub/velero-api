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

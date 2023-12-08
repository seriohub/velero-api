import json
from fastapi.responses import JSONResponse

from libs.process_v1 import *

from helpers.commons import *


class RepoV1:

    @handle_exceptions_async_method
    async def get(self, json_response=True):
        output = await run_process_check_output(['velero', 'repo', 'get', '-o', 'json'])
        if 'error' in output:
            return output

        repos = json.loads(output['data'])

        if repos['kind'].lower() == 'backuprepository':
            repos = {'items': [repos]}

        add_id_to_list(repos['items'])

        res = {'data': {'payload': repos}}
        if json_response:
            return JSONResponse(content=res, status_code=201, headers={'X-Custom-Header': 'header-value'})
        else:
            return repos

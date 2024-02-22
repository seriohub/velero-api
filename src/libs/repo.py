import json
import os

from dotenv import load_dotenv
from fastapi.responses import JSONResponse

from libs.process import *

from helpers.commons import *

load_dotenv()
class Repo:

    @handle_exceptions_async_method
    async def get(self, json_response=True):
        output = await run_process_check_output(['velero', 'repo', 'get', '-o', 'json',
                                                 '-n', os.getenv('K8S_VELERO_NAMESPACE', 'velero')])
        if 'error' in output:
            return output

        repos = json.loads(output['data'])

        if repos['kind'].lower() == 'backuprepository':
            repos = {'items': [repos]}

        add_id_to_list(repos['items'])

        res = {'data': {'payload': repos}}
        if json_response:
            return JSONResponse(content=res, status_code=201)
        else:
            return repos

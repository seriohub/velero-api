import json
from fastapi.responses import JSONResponse

from libs.process_v1 import *

from helpers.commons import *
from helpers.handle_exceptions import *


class SnapshotLocationV1:

    @handle_exceptions_async_method
    async def get(self, json_response=True):
        output = await run_process_check_output(['velero', 'snapshot-location', 'get', '-o', 'json'])
        if 'error' in output:
            return output

        snapshot_location = json.loads(output['data'])

        if snapshot_location['kind'].lower() == 'volumesnapshotlocation':
            snapshot_location = {'items': [snapshot_location]}

        add_id_to_list(snapshot_location['items'])

        res = {'data': {'payload': snapshot_location}}

        if json_response:
            return JSONResponse(content=res, status_code=201, headers={'X-Custom-Header': 'header-value'})
        else:
            return snapshot_location

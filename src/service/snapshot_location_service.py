import json
import os

from utils.commons import add_id_to_list
from utils.process import run_process_check_output
from utils.handle_exceptions import handle_exceptions_async_method

class SnapshotLocationService:

    @handle_exceptions_async_method
    async def get(self):
        output = await run_process_check_output(['velero', 'snapshot-location', 'get', '-o', 'json',
                                                 '-n', os.getenv('K8S_VELERO_NAMESPACE', 'velero')])
        if not output['success']:
            return output

        snapshot_location = json.loads(output['data'])

        if snapshot_location['kind'].lower() == 'volumesnapshotlocation':
            snapshot_location = {'items': [snapshot_location]}

        add_id_to_list(snapshot_location['items'])

        return {'success': True, 'data': snapshot_location['items']}

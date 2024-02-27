import json
import os

from utils.process import run_process_check_output
from utils.commons import add_id_to_list
from utils.handle_exceptions import handle_exceptions_async_method


class BackupLocationService:

    @handle_exceptions_async_method
    async def get(self):
        output = await run_process_check_output(['velero', 'backup-location', 'get', '-o', 'json',
                                                 '-n', os.getenv('K8S_VELERO_NAMESPACE', 'velero')])
        if not output['success']:
            return output

        backup_location = json.loads(output['data'])

        if backup_location['kind'].lower() == 'backupstoragelocation':
            backup_location = {'items': [backup_location]}

        add_id_to_list(backup_location['items'])

        return {'success': True, 'data': backup_location['items']}

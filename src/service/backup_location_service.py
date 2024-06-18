import json
import os

from utils.process import run_process_check_output
from utils.commons import add_id_to_list
from utils.handle_exceptions import handle_exceptions_async_method
from service.k8s_service import K8sService

ks8service = K8sService()

class BackupLocationService:

    @handle_exceptions_async_method
    async def get(self, backup_storage_location=None):
        if backup_storage_location is not None:
            cmd = ['velero', 'backup-location', 'get', backup_storage_location, '-o', 'json',
                                                     '-n', os.getenv('K8S_VELERO_NAMESPACE', 'velero')]
        else:
            cmd = ['velero', 'backup-location', 'get', '-o', 'json',
                   '-n', os.getenv('K8S_VELERO_NAMESPACE', 'velero')]
        output = await run_process_check_output(cmd)
        if not output['success']:
            return output

        backup_location = json.loads(output['data'])

        if backup_location['kind'].lower() == 'backupstoragelocation':
            backup_location = {'items': [backup_location]}

        add_id_to_list(backup_location['items'])

        return {'success': True, 'data': backup_location['items']}

    async def credentials(self, backup_storage_location):
        bsl = await self.get(backup_storage_location)
        try:
            if bsl.get('data') and isinstance(bsl['data'], list) and len(bsl['data']) > 0:
                credential_spec = bsl['data'][0].get('spec', {}).get('credential')
            else:
                credential_spec = None
            if credential_spec:
                output = await ks8service.get_credential(credential_spec['name'], credential_spec['key'])
            else:
                output = await ks8service.get_default_credential()
            secret_name = output['data']['aws_access_key_id']
            secret_key = output['data']['aws_secret_access_key']
            return secret_name, secret_key
        except:
            return '', ''


    @staticmethod
    def get_aws_key_id():
        return os.getenv("AWS_ACCESS_KEY_ID", "")

    @staticmethod
    def get_aws_access_key():
        return os.getenv("AWS_SECRET_ACCESS_KEY", "")
import json
import os

from api.v1.schemas.create_vsl import CreateVsl
from utils.handle_exceptions import handle_exceptions_async_method
# from utils.commons import add_id_to_list
from utils.process import run_process_check_output, run_process_check_call


from service.k8s_service import K8sService

k8sService = K8sService()

class SnapshotLocationService:

    @handle_exceptions_async_method
    async def get(self):
        output = await run_process_check_output(
            ['velero', 'snapshot-location', 'get', '-o', 'json', '-n', os.getenv('K8S_VELERO_NAMESPACE', 'velero')])
        if not output['success']:
            return output

        snapshot_location = json.loads(output['data'])

        if snapshot_location['kind'].lower() == 'volumesnapshotlocation':
            snapshot_location = {'items': [snapshot_location]}

        # add_id_to_list(snapshot_location['items'])

        return {'success': True, 'data': snapshot_location['items']}

    @handle_exceptions_async_method
    async def create(self, create_vsl: CreateVsl):

        cmd = ['velero', 'snapshot-location', 'create', create_vsl.name, '--provider', create_vsl.provider]

        if create_vsl.config and len(create_vsl.config) > 0:
            for config in create_vsl.config:
                cmd += ['--config', f"""{config['key']}={config['value']}"""]

        elif create_vsl.credentialSecretName != '':
            cmd += ['--credential', create_vsl.credentialSecretName + '=' + create_vsl.credentialKey]

        output = await run_process_check_output(cmd)

        if not output['success']:
            return output

        return {'success': True}

    @handle_exceptions_async_method
    async def delete(self, vsl_name):
        output = await k8sService.delete_volume_snapshot_location(vsl_name)
        print(output)
        if not output['success']:
            return output

        return {'success': True}

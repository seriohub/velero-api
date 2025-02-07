import json
import os

from utils.process import run_process_check_output, run_process_check_call
# from utils.commons import add_id_to_list

from api.v1.schemas.create_bsl import CreateBsl

from utils.handle_exceptions import handle_exceptions_async_method

from service.k8s_service import K8sService

ks8service = K8sService()


class BackupLocationService:

    @handle_exceptions_async_method
    async def get(self, backup_storage_location=None):
        if backup_storage_location is not None:
            cmd = ['velero', 'backup-location', 'get', backup_storage_location, '-o', 'json', '-n',
                   os.getenv('K8S_VELERO_NAMESPACE', 'velero')]
        else:
            cmd = ['velero', 'backup-location', 'get', '-o', 'json', '-n', os.getenv('K8S_VELERO_NAMESPACE', 'velero')]
        output = await run_process_check_output(cmd)
        if not output['success']:
            return output

        backup_location = json.loads(output['data'])

        if backup_location['kind'].lower() == 'backupstoragelocation':
            backup_location = {'items': [backup_location]}

        # add_id_to_list(backup_location['items'])

        return {'success': True, 'data': backup_location['items']}

    @handle_exceptions_async_method
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

    @handle_exceptions_async_method
    async def create(self, create_bsl: CreateBsl):
        # if create_bsl.newSecretName and create_bsl.newSecretName != '':
        #     await ks8service.create_cloud_credentials_secret(create_bsl.newSecretName,
        #                                                      create_bsl.awsAccessKeyId,
        #                                                      create_bsl.awsSecretAccessKey)
        cmd = ['velero', 'backup-location', 'create', create_bsl.name, '--provider', create_bsl.provider, '--bucket',
               create_bsl.bucketName, '--access-mode', create_bsl.accessMode, ]

        # if create_bsl.region and create_bsl.region != '':
        #     cmd += ['--config', 'region=' + create_bsl.region]
        # if create_bsl.s3Url and create_bsl.s3Url != '':
        #     cmd += ['--config', 's3Url='+create_bsl.s3Url]

        if create_bsl.config and len(create_bsl.config) > 0:
            for config in create_bsl.config:
                cmd += ['--config', f"""{config['key']}={config['value']}"""]

        if create_bsl.default:
            cmd.append('--default')

        if create_bsl.newSecretName and create_bsl.newSecretName != '':
            cmd += ['--credential', create_bsl.newSecretName + '=' + create_bsl.newSecretKey]
        elif create_bsl.credentialSecretName != '':
            cmd += ['--credential', create_bsl.credentialSecretName + '=' + create_bsl.credentialKey]

        output = await run_process_check_output(cmd)

        if not output['success']:
            return output

        return {'success': True}

    @handle_exceptions_async_method
    async def delete(self, bsl_name):
        output = await run_process_check_call(['velero', 'backup-location', 'delete', bsl_name, '--confirm', '-n',
                                               os.getenv('K8S_VELERO_NAMESPACE', 'velero')])
        if not output['success']:
            return output

        return {'success': True}

    @handle_exceptions_async_method
    async def default(self, bsl_name, default):
        output = await run_process_check_call(
            ['velero', 'backup-location', 'set', bsl_name, f"--default={str(default).lower()}"])
        if not output['success']:
            return output

        return {'success': True}

    @handle_exceptions_async_method
    async def remove_current_default(self):
        bsls = await self.get()
        print(bsls)
        for bsl in bsls['data']:
            if 'default' in bsl['spec'] and bsl['spec']['default']:
                await self.remove_default(bsl['metadata']['name'])

    @handle_exceptions_async_method
    async def remove_default(self, bsl_name):
        output = await run_process_check_call(['velero', 'backup-location', 'set', bsl_name, '--default=false'])
        if not output['success']:
            return output
        return {'success': True}

    # @staticmethod  # def get_aws_key_id():  #     return os.getenv("AWS_ACCESS_KEY_ID", "")

    # @staticmethod  # def get_aws_access_key():  #     return os.getenv("AWS_SECRET_ACCESS_KEY", "")

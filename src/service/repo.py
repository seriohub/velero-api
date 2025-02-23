import re

from fastapi import HTTPException

from models.k8s.repo import BackupRepositoryResponseSchema

from utils.minio_wrapper import MinioInterface
from utils.process import run_check_output_process

from kubernetes import client

from utils.logger_boot import logger

from configs.config_boot import config_app
from configs.velero import VELERO
from configs.resources import RESOURCES, ResourcesNames

custom_objects = client.CustomObjectsApi()


async def get_repos_service():
    repos = custom_objects.list_namespaced_custom_object(
        group=VELERO["GROUP"],
        version=VELERO["VERSION"],
        namespace=config_app.get_k8s_velero_namespace(),
        plural=RESOURCES[ResourcesNames.BACKUP_REPOSITORY].plural
    )

    bsl_list = [BackupRepositoryResponseSchema(**item) for item in repos.get("items", [])]

    return bsl_list


async def get_repo_backup_size_service(repository_url: str = None,
                                       backup_storage_location: str = None,
                                       repository_name: str = None,
                                       repository_type: str = None,
                                       volume_namespace: str = None):
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

    return await minio_interface.get_backup_size(repository_url=repository_url,
                                                 endpoint=endpoint,
                                                 backup_storage_location=backup_storage_location,
                                                 bucket_name=bucket_name,
                                                 repository_name=repository_name,
                                                 repository_type=repository_type,
                                                 volume_namespace=volume_namespace)


async def get_repo_locks_service(env, repository_url):
    cmd = ['restic', '-q', '--no-lock', 'list', 'locks', '-r', repository_url]

    output = await run_check_output_process(cmd=cmd, env=env)

    if not output['success']:
        raise HTTPException(status_code=400, detail=f'Error get repo locks service')

    locks = output['data']

    return {str(repository_url): list(filter(None, locks.split('\n')))}


async def unlock_repo_service(env, bsl, repository_url, remove_all=False):
    cmd = ['restic', 'unlock', '-r', repository_url]
    if remove_all:
        cmd.append('--remove-all')

    output = await run_check_output_process(cmd=cmd, env=env)

    if not output['success']:
        raise HTTPException(status_code=400, detail=f'Error unlock repo locks service')

    locks = output['data']

    return {'bsl': bsl,
            'repositoryUrl': str(repository_url),
            'locks': list(filter(None, locks.split('\n')))}


async def check_repo_service(env, repository_url):
    cmd = ['restic', 'check', '-r', repository_url]

    output = await run_check_output_process(cmd=cmd, env=env)

    if not output['success']:
        raise HTTPException(status_code=400, detail=f'Error check repo locks service')

    check = output['data']

    return {str(repository_url): list(filter(None, check.split('\n')))}

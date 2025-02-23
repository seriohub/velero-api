from service.bsl import get_bsls_service
from service.k8s import get_namespaces_service, get_resources_service
from service.vsl import get_vsls_service


async def get_backup_creation_settings_service():
    namespaces = (await get_namespaces_service())
    backup_location = await get_bsls_service()
    snapshot_location = await get_vsls_service()
    backup_location_list = [item['metadata']['name'] for item in backup_location if
                            'metadata' in item and 'name' in item['metadata']]
    snapshot_location_list = [item['metadata']['name'] for item in snapshot_location if
                              'metadata' in item and 'name' in item['metadata']]
    valid_resources = (await get_resources_service())

    payload = {'namespaces': namespaces,
               'backup_location': backup_location_list,
               'snapshot_location': snapshot_location_list,
               'resources': valid_resources}

    return payload

from service.bsl import get_bsls_service
from service.k8s import get_namespaces_service, get_resources_service
from service.k8s_configmap import list_configmaps_service
from service.vsl import get_vsls_service
from utils.k8s_tracer import trace_k8s_async_method


@trace_k8s_async_method(description="Get backup/schedule creation settings")
async def get_resource_creation_settings_service():
    namespaces = await get_namespaces_service()
    bsls = await get_bsls_service()
    vsls = await get_vsls_service()

    bsls = [bsl.model_dump() for bsl in bsls]
    vsls = [vsl.model_dump() for vsl in vsls]

    resource_policy = list_configmaps_service()

    backup_location_list = [item['metadata']['name'] for item in bsls if
                            'metadata' in item and 'name' in item['metadata']]
    snapshot_location_list = [item['metadata']['name'] for item in vsls if
                              'metadata' in item and 'name' in item['metadata']]
    valid_resources = (await get_resources_service())

    payload = {'namespaces': namespaces,
               'backup_location': backup_location_list,
               'snapshot_location': snapshot_location_list,
               'resources': valid_resources,
               'resource_policy': resource_policy
               }

    return payload

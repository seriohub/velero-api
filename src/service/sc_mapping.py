import os

from fastapi import HTTPException
from kubernetes import client
from kubernetes.client.exceptions import ApiException

from configs.config_boot import config_app

from utils.k8s_tracer import trace_k8s_async_method
from utils.logger_boot import logger

core_v1 = client.CoreV1Api()
custom_object = client.CustomObjectsApi()
storage_v1 = client.StorageV1Api()


@trace_k8s_async_method(description="Set storage class map")
async def __set_storages_classes_map(namespace=os.getenv('K8S_VELERO_NAMESPACE', 'velero'),
                                     config_map_name='change-storage-classes-config',
                                     data_list=None):
    if data_list is None:
        data_list = {}
    else:
        tmp = {}
        for item in data_list:
            tmp[item['oldStorageClass']] = item['newStorageClass']
        data_list = tmp
    try:

        # ConfigMap metadata
        config_map_metadata = client.V1ObjectMeta(
            name=config_map_name,
            namespace=namespace,
            labels={
                "velero.io/plugin-config": "",
                "velero.io/change-storage-class": "RestoreItemAction"
            }
        )

        # Check if the ConfigMap already exists
        try:
            existing_config_map = core_v1.read_namespaced_config_map(name=config_map_name,
                                                                     namespace=namespace)

            # If it exists, update the ConfigMap
            existing_config_map.data = data_list
            core_v1.replace_namespaced_config_map(name=config_map_name, namespace=namespace,
                                                  body=existing_config_map)
            logger.info(
                "ConfigMap 'change-storage-class-config' in namespace 'velero' updated successfully.")
        except client.rest.ApiException as e:
            # If it doesn't exist, create the ConfigMap
            if e.status == 404:
                config_map_body = client.V1ConfigMap(
                    metadata=config_map_metadata,
                    data=data_list
                )
                core_v1.create_namespaced_config_map(namespace=namespace, body=config_map_body)
                logger.info(
                    "ConfigMap 'change-storage-class-config' in namespace 'velero' created successfully.")
            else:
                raise e
    except Exception as e:
        logger.error(f"Error writing ConfigMap 'change-storage-class-config' in namespace 'velero': {e}")


@trace_k8s_async_method(description="Get storage class config map")
async def get_storages_classes_map_service(config_map_name='change-storage-classes-config',
                                           namespace=os.getenv('K8S_VELERO_NAMESPACE', 'velero')):
    # Create an instance of the Kubernetes core API

    # Get the ConfigMap
    try:
        config_map = core_v1.read_namespaced_config_map(name=config_map_name,
                                                        namespace=namespace)  # Extract data from the ConfigMap
        data = config_map.data or {}
    except ApiException as e:
        if e.status == 404:
            # err_msg = f"ConfigMap '{config_map_name}' not found in namespace '{namespace}'"
            logger.warning(f"{e.status} Error reading ConfigMap '{config_map_name}' in namespace '{namespace}'")
            return []
        else:
            # err_msg = f"Error reading ConfigMap '{config_map_name}' in namespace '{namespace}': {e}"
            logger.warning(f"{e.status} Error reading ConfigMap '{config_map_name}' in namespace '{namespace}'")
            return []

    if len(data.items()) > 0:
        data_list = [{"oldStorageClass": key, "newStorageClass": value} for key, value in data.items()]
        # add_id_to_list(data_list)
    else:
        data_list = []

    return data_list


@trace_k8s_async_method(description="Update storage classes map")
async def update_storages_classes_mapping_service(data_list=None):
    if data_list is not None:
        payload = await get_storages_classes_map_service()
        config_map = payload
        exists = False
        for item in config_map:
            item.pop('id', None)
            if item['oldStorageClass'] == data_list['oldStorageClass']:
                item['newStorageClass'] = data_list['newStorageClass']
                exists = True
        if not exists:
            config_map.append({'oldStorageClass': data_list['oldStorageClass'],
                               'newStorageClass': data_list['newStorageClass']})
        await __set_storages_classes_map(data_list=config_map)

        return True

    raise HTTPException(status_code=400, detail=f'Update storage classes error')


@trace_k8s_async_method(description="Delete storage classes map")
async def delete_storages_classes_mapping_service(data_list=None):
    if data_list is not None:
        payload = await get_storages_classes_map_service()
        config_map = payload
        for item in config_map:
            item.pop('id', None)
            if item['oldStorageClass'] == data_list['oldStorageClass'] and item['newStorageClass'] == data_list['newStorageClass']:
                config_map.remove(item)

        await __set_storages_classes_map(data_list=config_map)
        return True

    raise HTTPException(status_code=400, detail=f'Delete storage classes error')

import os
from kubernetes import client, config
from kubernetes.client.exceptions import ApiException

from core.config import ConfigHelper

from utils.commons import add_id_to_list
from utils.handle_exceptions import handle_exceptions_async_method
from utils.k8s_tracer import trace_k8s_async_method

from helpers.printer import PrintHelper


class ScMappingService:

    def __init__(self):

        if os.getenv('K8S_IN_CLUSTER_MODE').lower() == 'true':
            config.load_incluster_config()
        else:
            self.kube_config_file = os.getenv('KUBE_CONFIG_FILE')
            config.load_kube_config(config_file=self.kube_config_file)

        self.v1 = client.CoreV1Api()
        self.client = client.CustomObjectsApi()
        self.client_cs = client.StorageV1Api()
        config_app = ConfigHelper()
        self.print_ls = PrintHelper('[service.sc_mapping_service]',
                                    level=config_app.get_internal_log_level())

    @trace_k8s_async_method(description="Set storage class map")
    async def __set_storages_classes_map(self,
                                         namespace=os.getenv('K8S_VELERO_NAMESPACE', 'velero'),
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
            # Create an instance of the Kubernetes core API
            core_v1 = self.v1

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
                self.print_ls.info(
                    "ConfigMap 'change-storage-class-config' in namespace 'velero' updated successfully.")
            except client.rest.ApiException as e:
                # If it doesn't exist, create the ConfigMap
                if e.status == 404:
                    config_map_body = client.V1ConfigMap(
                        metadata=config_map_metadata,
                        data=data_list
                    )
                    core_v1.create_namespaced_config_map(namespace=namespace, body=config_map_body)
                    self.print_ls.info(
                        "ConfigMap 'change-storage-class-config' in namespace 'velero' created successfully.")
                else:
                    raise e
        except Exception as e:
            self.print_ls.error(f"Error writing ConfigMap 'change-storage-class-config' in namespace 'velero': {e}")

    @handle_exceptions_async_method
    @trace_k8s_async_method(description="get storage class config map")
    async def get_storages_classes_map(self,
                                       config_map_name='change-storage-classes-config',
                                       namespace=os.getenv('K8S_VELERO_NAMESPACE', 'velero')):

        # Create an instance of the Kubernetes core API
        core_v1 = self.v1  # client.CoreV1Api()

        # Get the ConfigMap
        try:
            config_map = core_v1.read_namespaced_config_map(name=config_map_name,
                                                            namespace=namespace)  # Extract data from the ConfigMap
            data = config_map.data or {}
        except ApiException as e:
            if e.status == 404:
                # err_msg = f"ConfigMap '{config_map_name}' not found in namespace '{namespace}'"
                self.print_ls.wrn(f"{e.status} Error reading ConfigMap '{config_map_name}' in namespace '{namespace}'")
                return {'success': True, 'data': []}
            else:
                # err_msg = f"Error reading ConfigMap '{config_map_name}' in namespace '{namespace}': {e}"
                self.print_ls.wrn(f"{e.status} Error reading ConfigMap '{config_map_name}' in namespace '{namespace}'")
                return {'success': True, 'data': []}

        if len(data.items()) > 0:
            data_list = [{"oldStorageClass": key, "newStorageClass": value} for key, value in data.items()]
            add_id_to_list(data_list)
        else:
            data_list = []

        return {'success': True, 'data': data_list}

    @handle_exceptions_async_method
    @trace_k8s_async_method(description="Update storage classes map")
    async def update_storages_classes_mapping(self,
                                              data_list=None):
        if data_list is not None:
            payload = await self.get_storages_classes_map()
            config_map = payload['data']
            exists = False
            for item in config_map:
                item.pop('id', None)
                if item['oldStorageClass'] == data_list['oldStorageClass']:
                    item['newStorageClass'] = data_list['newStorageClass']
                    exists = True
            if not exists:
                config_map.append({'oldStorageClass': data_list['oldStorageClass'],
                                   'newStorageClass': data_list['newStorageClass']})
            await self.__set_storages_classes_map(data_list=config_map)

            return {'success': True}

        return {'success': False, 'error': {'title': 'Error',
                                            'description': 'Data list empty'}
                }

    @handle_exceptions_async_method
    @trace_k8s_async_method(description="Delete storage classes map")
    async def delete_storages_classes_mapping(self,
                                              data_list=None):
        if data_list is not None:
            payload = await self.get_storages_classes_map()
            config_map = payload['data']
            for item in config_map:
                item.pop('id', None)
                if item['oldStorageClass'] == data_list['oldStorageClass'] and item['newStorageClass'] == data_list[
                    'newStorageClass']:
                    config_map.remove(item)

            await self.__set_storages_classes_map(data_list=config_map)
            return {'success': True}

        return {'success': True, 'error': {'title': 'Error',
                                           'description': 'Data list empty'}
                }

import os
from kubernetes import client, config
from dotenv import load_dotenv

from helpers.commons import *
from helpers.handle_exceptions import *
from fastapi.responses import JSONResponse
from kubernetes.client.exceptions import ApiException

load_dotenv()


class SCMapping:

    def __init__(self):

        if os.getenv('K8S_IN_CLUSTER_MODE').lower() == 'true':
            config.load_incluster_config()
        else:
            self.kube_config_file = os.getenv('KUBE_CONFIG_FILE')
            config.load_kube_config(config_file=self.kube_config_file)

        self.v1 = client.CoreV1Api()
        self.client = client.CustomObjectsApi()
        self.client_cs = client.StorageV1Api()

    @trace_k8s_async_method(description="get storage class config map")
    async def get_storages_classes_map(self, config_map_name='change-storage-classes-config',
                                       namespace=os.getenv('K8S_VELERO_NAMESPACE', 'velero'),
                                       json_response=True):
        try:
            # Create an instance of the Kubernetes core API
            core_v1 = self.v1  # client.CoreV1Api()
            data = {}
            # Get the ConfigMap
            try:
                config_map = core_v1.read_namespaced_config_map(name=config_map_name,
                                                                namespace=namespace)  # Extract data from the ConfigMap
                data = config_map.data or {}
            except ApiException as e:
                if e.status == 404:
                    err_msg = f"ConfigMap '{config_map_name}' not found in namespace '{namespace}'"
                    print(err_msg)
                    # err = {'error': {'description': err_msg}}
                    if json_response:
                        raise Exception(err_msg)
                    # return JSONResponse(content=err, status_code=404, headers={'X-Custom-Header': 'header-value'})
                else:
                    err_msg = f"Error reading ConfigMap '{config_map_name}' in namespace '{namespace}': {e}"
                    print(err_msg)
                    # err = {'error': {'description': err_msg}}
                    if json_response:
                        raise Exception(err_msg)
                    # return JSONResponse(content=err, status_code=422, headers={'X-Custom-Header': 'header-value'})

            # Convert data to a list of dictionaries
            # data_list = [{"key": key, "value": value} for key, value in data.items()]
            data_list = [{"oldStorageClass": key, "newStorageClass": value} for key, value in data.items()]
            if not json_response:
                return data_list

            add_id_to_list(data_list)
            res = {'data': data_list}
            return JSONResponse(content=res, status_code=201, headers={'X-Custom-Header': 'header-value'})

        except Exception as e:
            print(f"Error reading ConfigMap '{config_map_name}' in namespace '{namespace}': {e}")
            err = {'error': {
                'description': f"Error reading ConfigMap '{config_map_name}' in namespace '{namespace}': {e}"}
            }
            return JSONResponse(content=err, status_code=422, headers={'X-Custom-Header': 'header-value'})

    @handle_exceptions_instance_method
    @trace_k8s_async_method(description="Set storage class map")
    async def set_storages_classes_map(self,
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
                print("ConfigMap 'change-storage-class-config' in namespace 'velero' updated successfully.")
            except client.rest.ApiException as e:
                # If it doesn't exist, create the ConfigMap
                if e.status == 404:
                    config_map_body = client.V1ConfigMap(
                        metadata=config_map_metadata,
                        data=data_list
                    )
                    core_v1.create_namespaced_config_map(namespace=namespace, body=config_map_body)
                    print("ConfigMap 'change-storage-class-config' in namespace 'velero' created successfully.")
                else:
                    raise e
        except Exception as e:
            print(f"Error writing ConfigMap 'change-storage-class-config' in namespace 'velero': {e}")

    @handle_exceptions_instance_method
    @trace_k8s_async_method(description="Update storage classes map")
    async def update_storages_classes_mapping(self,
                                              data_list=None):
        if data_list is not None:
            config_map = await self.get_storages_classes_map(json_response=False)
            exists = False
            for item in config_map:
                item.pop('id', None)
                if item['oldStorageClass'] == data_list['oldStorageClass']:
                    item['newStorageClass'] = data_list['newStorageClass']
                    exists = True
            if not exists:
                config_map.append({'oldStorageClass': data_list['oldStorageClass'],
                                   'newStorageClass': data_list['newStorageClass']})
            await self.set_storages_classes_map(data_list=config_map)

            return {'messages': [{'title': 'Storage Class Mapping',
                                  'description': f"Done!",
                                  'type': 'info'
                                  }]
                    }

    @handle_exceptions_instance_method
    @trace_k8s_async_method(description="Delete storage classes map")
    async def delete_storages_classes_mapping(self,
                                              data_list=None):
        if data_list is not None:
            config_map = await self.get_storages_classes_map(json_response=False)
            for item in config_map:
                item.pop('id', None)
                if item['oldStorageClass'] == data_list['oldStorageClass'] and item['newStorageClass'] == data_list[
                    'newStorageClass']:
                    config_map.remove(item)

            await self.set_storages_classes_map(data_list=config_map)
            return {'messages': [{'title': 'Storage Class Mapping',
                                  'description': f"Done!",
                                  'type': 'info'
                                  }]
                    }

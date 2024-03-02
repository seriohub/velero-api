import os
import configparser
import base64
from kubernetes import client, config
from datetime import datetime

from core.config import ConfigHelper
from utils.k8s_tracer import trace_k8s_async_method
from utils.handle_exceptions import handle_exceptions_async_method
from helpers.printer import PrintHelper


class K8sService:
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
        self.print_ls = PrintHelper(['service.k8s'],
                                    level=config_app.get_internal_log_level())

    def __parse_config_string(self, config_string):

        # Create a ConfigParser object
        config_parser = configparser.ConfigParser()

        # read string
        config_parser.read_string(config_string)

        # extract values
        aws_access_key_id = config_parser.get('default', 'aws_access_key_id', fallback=None)
        aws_secret_access_key = config_parser.get('default', 'aws_secret_access_key', fallback=None)

        # crete dict
        result = {
            'aws_access_key_id': aws_access_key_id,
            'aws_secret_access_key': aws_secret_access_key
        }

        return result

    async def __get_node_list(self, only_problem=False):
        """
        Obtain K8S nodes
        :param only_problem:
        :return: List of nodes
        """
        try:
            total_nodes = 0
            retrieved_nodes = 0
            add_node = True
            nodes = {}
            active_context = ''
            # Listing the cluster nodes
            node_list = self.v1.list_node()
            for node in node_list.items:
                total_nodes += 1
                node_details = {}

                node_details['context'] = active_context
                node_details['name'] = node.metadata.name
                if 'kubernetes.io/role' in node.metadata.labels:
                    node_details['role'] = node.metadata.labels['kubernetes.io/role']

                    node_details['role'] = 'control-plane'
                version = node.status.node_info.kube_proxy_version
                node_details['version'] = version

                node_details['architecture'] = node.status.node_info.architecture

                node_details['operating_system'] = node.status.node_info.operating_system

                node_details['kernel_version'] = node.status.node_info.kernel_version

                node_details['os_image'] = node.status.node_info.os_image

                node_details['addresses'] = node.status.addresses
                condition = {}
                for detail in node.status.conditions:
                    condition[detail.reason] = detail.status

                    if only_problem:
                        if add_node:
                            if detail.reason == 'KubeletReady':
                                if not bool(detail.status):
                                    add_node = False
                            else:
                                if bool(detail.status):
                                    add_node = False
                    else:
                        add_node = True
                node_details['conditions'] = condition

                if add_node:
                    retrieved_nodes += 1
                    nodes[node.metadata.name] = node_details

            return total_nodes, retrieved_nodes, nodes

        except Exception as err:
            return 0, 0, None

    @handle_exceptions_async_method
    @trace_k8s_async_method(description="get storage classes")
    async def get_storage_classes(self):
        st_cla = {}
        sc_list = self.client_cs.list_storage_class()

        if sc_list is not None:
            for st in sc_list.items:
                v_class = {'name': st.metadata.name,
                           'provisioner': st.provisioner,
                           'parameters': st.parameters,
                           }

                st_cla[st.metadata.name] = v_class
            return {'success': True, 'data': st_cla}
        else:
            return {'success': False, 'error': {'title': 'error', 'description': 'Storage classes return data'}}

    @handle_exceptions_async_method
    @trace_k8s_async_method(description="get online data")
    async def get_k8s_online(self):
        ret = False
        total_nodes = 0
        retr_nodes = 0
        try:
            total_nodes, retr_nodes, nodes = await self.__get_node_list(only_problem=True)
            if nodes is not None:
                ret = True

        except Exception as Ex:
            ret = False

        output = {
            'cluster_online': ret,
            'nodes':
                {'total': total_nodes,
                 'in_error': retr_nodes
                 },

            'timestamp': str(datetime.utcnow())}
        return {'success': True, 'data': output}

    @handle_exceptions_async_method
    @trace_k8s_async_method(description="get configmap 'velero-api-config'")
    async def get_config_map(self, namespace):
        # Create a Kubernetes API client
        core_api = self.v1

        # Specify the namespace and the name of the ConfigMap you want to read
        # namespace = app_config.get_k8s_velero_ui_namespace()
        configmap_name = 'velero-api-config'

        try:
            # Retrieve the ConfigMap
            configmap = core_api.read_namespaced_config_map(name=configmap_name, namespace=namespace)

            # Access the data in the ConfigMap
            data = configmap.data
            kv = {}
            # Print out the data
            for key, value in data.items():
                if key.startswith('SECURITY_TOKEN_KEY'):
                    value = value[1].ljust(len(value) - 1, '*')
                kv[key] = value
            return {'success': True, 'data': kv}
        except client.exceptions.ApiException as e:
            self.print_ls.error(f"Exception when calling CoreV1Api->read_namespaced_config_map: {e}")
            return {'success': False, 'error': {'Title': 'get config map',
                                                'description': f"Exception when calling CoreV1Api->read_namespaced_config_map: {e}"
                                                }
                    }

    @handle_exceptions_async_method
    @trace_k8s_async_method(description="get namespaces")
    async def get_ns(self):
        # Get namespaces list
        namespace_list = self.v1.list_namespace()
        # Extract namespace list
        namespaces = [namespace.metadata.name for namespace in namespace_list.items]
        return {'success': True, 'data': namespaces}

    @handle_exceptions_async_method
    @trace_k8s_async_method(description="update velero schedule")
    async def update_velero_schedule(self, new_data):

        namespace = os.getenv('K8S_VELERO_NAMESPACE')

        velero_resource_name = new_data['oldName']

        try:
            # get resource velero
            velero_resource = self.client.get_namespaced_custom_object(
                group='velero.io',
                version='v1',
                name=velero_resource_name,
                namespace=namespace,
                plural='schedules',
            )

            # update field
            velero_resource['spec']['schedule'] = new_data['schedule']
            if 'includedNamespaces' in new_data:
                velero_resource['spec']['template']['includedNamespaces'] = new_data['includedNamespaces']
            if 'excludedNamespaces' in new_data:
                velero_resource['spec']['template']['excludedNamespaces'] = new_data['excludedNamespaces']
            if 'includedResources' in new_data:
                velero_resource['spec']['template']['includedResources'] = new_data['includedResources']
            if 'excludedResources' in new_data:
                velero_resource['spec']['template']['excludedResources'] = new_data['excludedResources']

            if 'includeClusterResources' in new_data:
                if new_data['includeClusterResources'] == 'true':
                    velero_resource['spec']['template']['includeClusterResources'] = True
                elif new_data['includeClusterResources'] == 'false':
                    velero_resource['spec']['template']['includeClusterResources'] = False
                else:
                    velero_resource['spec']['template']['includeClusterResources'] = None

            if 'backupLocation' in new_data:
                velero_resource['spec']['template']['storageLocation'] = new_data['backupLocation']

            if 'snapshotLocation' in new_data:
                velero_resource['spec']['template']['volumeSnapshotLocations'] = new_data['snapshotLocation']

            if 'snapshotVolumes' in new_data:
                velero_resource['spec']['template']['snapshotVolumes'] = new_data['snapshotVolumes']

            if 'defaultVolumesToFsBackup' in new_data:
                velero_resource['spec']['template']['defaultVolumesToFsBackup'] = new_data['defaultVolumesToFsBackup']

            if 'backupLevel' in new_data and 'selector' in new_data:
                if new_data['backupLabel'] != '' and new_data['selector'] != '':
                    if 'labelSelector' not in velero_resource['spec']['template']:
                        velero_resource['spec']['template']['labelSelector'] = {}
                    if 'matchLabels' not in velero_resource['spec']['template']['labelSelector']:
                        velero_resource['spec']['template']['labelSelector'] = {}
                    velero_resource['spec']['template']['labelSelector']['matchLabels'] = {
                        new_data['backupLabel']: new_data['selector']}

            # execute update data
            self.client.replace_namespaced_custom_object(
                group='velero.io',
                version='v1',
                name=velero_resource_name,
                namespace=namespace,
                plural='schedules',
                body=velero_resource,
            )

            return {'success': True}

        except Exception as e:
            return {'success': False, 'error': {'Title': 'Update velero schedule',
                                                'description': f"Error in updating Velero's schedule '{velero_resource_name}': {e}"}
                    }

    @handle_exceptions_async_method
    @trace_k8s_async_method(description="get resources")
    async def get_resources(self):
        # TODO: not working yet, get all resource type name for populate multiselect in front end
        resource_list = self.client.get_api_resources(group='*', version='*')

        return {'success': True, 'data': resource_list}

    @handle_exceptions_async_method
    @trace_k8s_async_method(description="get s3 credential")
    async def get_credential(self, secret_name, secret_key):

        api_instance = self.v1

        # LS 2024.20.22 use env variable
        # secret = api_instance.read_namespaced_secret(name=secret_name, namespace='velero')
        secret = api_instance.read_namespaced_secret(name=secret_name,
                                                     namespace=os.getenv('K8S_VELERO_NAMESPACE', 'velero'))
        if secret.data and secret_key in secret.data:
            value = secret.data[secret_key]
            decoded_value = base64.b64decode(value)
            payload = self.__parse_config_string(decoded_value.decode('utf-8'))
            return {'success': True, 'data': payload}
        else:
            return {'success': False, 'error': {'title': 'Error',
                                                'description': 'Secret key not found'}}

    @handle_exceptions_async_method
    @trace_k8s_async_method(description="get default s3 credential")
    async def get_default_credential(self):
        label_selector = 'app.kubernetes.io/name=velero'
        api_instance = self.v1

        secret = api_instance.list_namespaced_secret(namespace=os.getenv('K8S_VELERO_NAMESPACE', 'velero'),
                                                     label_selector=label_selector)

        if secret.items[0].data:
            value = secret.items[0].data['cloud']
            decoded_value = base64.b64decode(value)

            payload = self.__parse_config_string(decoded_value.decode('utf-8'))

            return {'success': True, 'data': payload}
        else:
            return {'success': False, 'error': {'title': "Error",
                                                "description": "Secret key not found"}
                    }

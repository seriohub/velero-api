import os
import configparser
import base64
from kubernetes import client, config
from kubernetes.client import ApiException
from datetime import datetime

from core.config import ConfigHelper
from utils.k8s_tracer import trace_k8s_async_method
from utils.handle_exceptions import handle_exceptions_async_method
from helpers.printer import PrintHelper
import sys


class K8sService:
    def __init__(self):

        if os.getenv('K8S_IN_CLUSTER_MODE').lower() == 'true':
            config.load_incluster_config()
        else:
            self.kube_config_file = os.getenv('KUBE_CONFIG_FILE')
            config.load_kube_config(config_file=self.kube_config_file)

        # self.coreV1Api = client.CoreV1Api()
        # self.batchV1Api = client.BatchV1Api()
        # self.customObjectsApi = client.CustomObjectsApi()
        # self.storageV1Api = client.StorageV1Api()

        self.config_app = ConfigHelper()
        self.print_ls = PrintHelper(['service.k8s'], level=self.config_app.get_internal_log_level())

    @staticmethod
    def __parse_config_string(config_string):

        # Create a ConfigParser object
        config_parser = configparser.ConfigParser()

        # read string
        config_parser.read_string(config_string)

        # extract values
        aws_access_key_id = config_parser.get('default', 'aws_access_key_id', fallback=None)
        aws_secret_access_key = config_parser.get('default', 'aws_secret_access_key', fallback=None)

        # crete dict
        result = {'aws_access_key_id': aws_access_key_id, 'aws_secret_access_key': aws_secret_access_key}

        return result

    @staticmethod
    def __transform_logs_to_json(logs):
        json_logs = []
        for log_line in logs.split("\n"):
            if log_line.strip():
                log_entry = {"log": log_line}
                json_logs.append(log_entry)
        return json_logs

    @staticmethod
    async def __get_node_list(only_problem=False):
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
            node_list = client.CoreV1Api().list_node()
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
        storage_classes = {}

        storage_classes_list = client.StorageV1Api().list_storage_class()

        if storage_classes_list is not None:
            for sc in storage_classes_list.items:
                v_class = {'name': sc.metadata.name, 'provisioner': sc.provisioner, 'parameters': sc.parameters, }
                storage_classes[sc.metadata.name] = v_class

            return {'success': True, 'data': storage_classes}
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

        output = {'cluster_online': ret, 'nodes': {'total': total_nodes, 'in_error': retr_nodes},

                  'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')}
        return {'success': True, 'data': output}

    @handle_exceptions_async_method
    @trace_k8s_async_method(description="get configmap")
    async def get_config_map(self, namespace, configmap_name):
        # Kubernetes API client
        core_api = client.CoreV1Api()

        # Specify the namespace and the name of the ConfigMap you want to read
        # namespace = app_config.get_k8s_velero_ui_namespace()
        # configmap_name = 'velero-api-config'

        try:
            # Retrieve the ConfigMap
            configmap = core_api.read_namespaced_config_map(name=configmap_name, namespace=namespace)

            # Access the data in the ConfigMap
            data = configmap.data
            kv = {}
            # Print out the data
            for key, value in data.items():
                if (key.startswith('SECURITY_TOKEN_KEY') or key.startswith('AWS_SECRET_ACCESS_KEY') or
                        key.startswith('EMAIL_PASSWORD') or key.startswith('TELEGRAM_TOKEN')):
                    value = value[0].ljust(len(value) - 1, '*')
                kv[key] = value
            return {'success': True, 'data': kv}
        except client.exceptions.ApiException as e:
            self.print_ls.error(f"Exception when calling CoreV1Api->read_namespaced_config_map: {e}")
            return {'success': False, 'error': {'Title': 'get config map',
                                                'description': f"Exception when calling "
                                                               f"CoreV1Api->read_namespaced_config_map: {e}"}}

    @handle_exceptions_async_method
    @trace_k8s_async_method(description="get namespaces")
    async def get_ns(self):
        # Get namespaces list
        namespace_list = client.CoreV1Api().list_namespace()
        # Extract namespace list
        namespaces = [namespace.metadata.name for namespace in namespace_list.items]
        return {'success': True, 'data': namespaces}

    @handle_exceptions_async_method
    @trace_k8s_async_method(description="update velero schedule")
    async def update_velero_schedule(self, new_data):

        namespace = os.getenv('K8S_VELERO_NAMESPACE')

        velero_resource_name = new_data.oldName

        try:
            # get resource velero
            velero_resource = client.CustomObjectsApi().get_namespaced_custom_object(group='velero.io',
                                                                                     version='v1',
                                                                                     name=velero_resource_name,
                                                                                     namespace=namespace,
                                                                                     plural='schedules')

            # update field
            velero_resource['spec']['schedule'] = new_data.schedule
            if new_data.includedNamespaces != '':
                velero_resource['spec']['template']['includedNamespaces'] = new_data.includedNamespaces
            if new_data.excludedNamespaces != '':
                velero_resource['spec']['template']['excludedNamespaces'] = new_data.excludedNamespaces
            if new_data.includedResources != '':
                velero_resource['spec']['template']['includedResources'] = new_data.includedResources
            if new_data.excludedResources != '':
                velero_resource['spec']['template']['excludedResources'] = new_data.excludedResources

            if new_data.includeClusterResources:
                if new_data.includeClusterResources == 'true':
                    velero_resource['spec']['template']['includeClusterResources'] = True
                elif new_data.includeClusterResources == 'false':
                    velero_resource['spec']['template']['includeClusterResources'] = False
                else:
                    velero_resource['spec']['template']['includeClusterResources'] = None

            if new_data.backupLocation != '':
                velero_resource['spec']['template']['storageLocation'] = new_data.backupLocation

            if len(new_data.snapshotLocation) > 0:
                velero_resource['spec']['template']['volumeSnapshotLocations'] = new_data.snapshotLocation

            if bool(new_data.snapshotVolumes):
                velero_resource['spec']['template']['snapshotVolumes'] = new_data.snapshotVolumes

            if bool(new_data.defaultVolumesToFsBackup):
                velero_resource['spec']['template']['defaultVolumesToFsBackup'] = new_data.defaultVolumesToFsBackup

            if new_data.backupLabel != '' and new_data.selector != '':
                if 'labelSelector' not in velero_resource['spec']['template']:
                    velero_resource['spec']['template']['labelSelector'] = {}
                if 'matchLabels' not in velero_resource['spec']['template']['labelSelector']:
                    velero_resource['spec']['template']['labelSelector'] = {}
                velero_resource['spec']['template']['labelSelector']['matchLabels'] = {
                    new_data.backupLabel: new_data.selector}

            # execute update data
            client.CustomObjectsApi().replace_namespaced_custom_object(group='velero.io',
                                                                       version='v1',
                                                                       name=velero_resource_name,
                                                                       namespace=namespace,
                                                                       plural='schedules',
                                                                       body=velero_resource)

            return {'success': True}

        except Exception as e:
            return {'success': False, 'error': {'Title': 'Update velero schedule',
                                                'description': f"Error in updating Vele"
                                                               f"ro's schedule '{velero_resource_name}': {e}"}}

    @handle_exceptions_async_method
    @trace_k8s_async_method(description="get resources")
    async def get_resources(self):
        self.print_ls.info(f"load_resources")
        try:

            valid_resources = []

            k8s_client = client
            # Initialize the API client
            api_client = k8s_client.ApiClient()

            # # Retrieve the list of available API groups
            # discovery = k8s_client.ApisApi(api_client)
            # api_groups = discovery.get_api_versions().groups

            # Retrieve the list of available API groups
            discovery = k8s_client.ApisApi(api_client)
            try:
                api_groups = discovery.get_api_versions().groups
                self.print_ls.debug(f"Retrieved API groups with success")
            except ApiException as e:
                self.print_ls.error_and_exception(f"Exception when retrieving API groups", e)
                return valid_resources

            for group in api_groups:
                self.print_ls.debug(f"find. apihist  group: {group.name}")
                for version in group.versions:
                    group_version = f"{group.name}/{version.version}" if group.name else version.version
                    try:
                        self.print_ls.debug(f"API group version: {group_version}")
                        # Get the resources for the group version
                        # api_resources = api_client.call_api(
                        #     f'/apis/{group_version}', 'GET',
                        #     response_type='object')[0]['resources']
                        #
                        # for resource in api_resources:
                        #     if '/' not in resource['name']:  # Only include resource names, not sub-resources
                        #         if resource['name'] not in valid_resources:
                        #             valid_resources.append(resource['name'])
                        # Use the Kubernetes client to get the resources
                        api_instance = k8s_client.CustomObjectsApi(api_client)
                        api_resources = api_instance.list_cluster_custom_object(group=group.name,
                                                                                version=version.version, plural='').get(
                            'resources', [])

                        for resource in api_resources:
                            if '/' not in resource['name']:  # Only include resource names, not sub-resources
                                if resource['name'] not in valid_resources:
                                    valid_resources.append(resource['name'])

                    except k8s_client.exceptions.ApiException as e:
                        self.print_ls.error(
                            f"Exception when calling ApisApi->get_api_resources for {group_version}: {e}")
                        continue

            # Get core API resources
            core_api = k8s_client.CoreV1Api(api_client)
            core_resources = core_api.get_api_resources().resources
            for resource in core_resources:
                if '/' not in resource.name:  # Only include resource names, not sub-resources
                    # valid_resources.append(resource.name)
                    if resource.name not in valid_resources:
                        valid_resources.append(resource.name)

            # If you want to maintain the order of elements as they were added to the set
            if len(valid_resources):
                res_list_ordered = sorted(list(valid_resources))
                self.print_ls.trace(f"load_resources:{res_list_ordered}")
                return {'success': True, 'data': res_list_ordered}
            else:
                self.print_ls.wrn(f"load_load_resources:No load_resources found")
                return {'success': False, 'data': []}

        except Exception as Ex:
            self.print_ls.error(sys.exc_info() + Ex)
            return {'success': False, 'data': []}

    @handle_exceptions_async_method
    @trace_k8s_async_method(description="get s3 credential")
    async def get_credential(self, secret_name, secret_key):
        api_instance = client.CoreV1Api()

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
            return {'success': False, 'error': {'title': 'Error', 'description': 'Secret key not found'}}

    @handle_exceptions_async_method
    @trace_k8s_async_method(description="get default s3 credential")
    async def get_default_credential(self):
        label_selector = 'app.kubernetes.io/name=velero'
        api_instance = client.CoreV1Api()

        secret = api_instance.list_namespaced_secret(namespace=os.getenv('K8S_VELERO_NAMESPACE', 'velero'),
                                                     label_selector=label_selector)

        if secret.items[0].data:
            value = secret.items[0].data['cloud']
            decoded_value = base64.b64decode(value)

            payload = self.__parse_config_string(decoded_value.decode('utf-8'))

            return {'success': True, 'data': payload}
        else:
            return {'success': False, 'error': {'title': "Error", "description": "Secret key not found"}}

    @handle_exceptions_async_method
    @trace_k8s_async_method(description="get logs")
    async def get_logs(self, lines=100, follow=False):
        # Get env variable data
        namespace = self.config_app.k8s_pod_namespace_in() or []
        pod_name = self.config_app.k8s_pod_name() or []
        in_cluster_mode = self.config_app.k8s_in_cluster_mode()

        if lines < 10:
            lines = 100
        elif lines > 500:
            lines = 500

        if in_cluster_mode:
            if len(namespace) > 0 and len(pod_name) > 0:
                # Retrieve logs from the pod
                logs = client.CoreV1Api().read_namespaced_pod_log(namespace=namespace,
                                                                  name=pod_name,
                                                                  pretty=True,
                                                                  # If the pod has only one container, you can omit this
                                                                  container=None,
                                                                  # Include timestamps in the logs
                                                                  timestamps=False,
                                                                  # Number of lines to retrieve from the end of the logs
                                                                  tail_lines=lines,
                                                                  # Set to True if you want to follow the logs
                                                                  # continuously
                                                                  follow=follow)
                if logs is not None:
                    # Transform logs to JSON format
                    json_logs = self.__transform_logs_to_json(logs)
                    return {'success': True, 'data': json_logs}
                else:
                    return {'success': False, 'error': {'title': "Error", "description": f"No logs retrieved "
                                                                                         f"pod name {pod_name} in"
                                                                                         f" the namespace {namespace} "
                                                                                         f""}}
            else:
                return {'success': False, 'error': {'title': "Error", "description": f"Namespace (par:{namespace}) "
                                                                                     f"or pod_name(par:{pod_name}) "
                                                                                     f"not defined."}}
        else:
            return {'success': False,
                    'error': {'title': "Error", "description": f"the application is not running in container mode."}}

    @handle_exceptions_async_method
    @trace_k8s_async_method(description="get cron schedule")
    async def get_cron_schedule(self, namespace, job_name):
        try:
            api_instance = client.BatchV1Api()
            self.print_ls.debug(f"namespace {namespace} job_name {job_name}")
            cronjob = api_instance.read_namespaced_cron_job(name=job_name, namespace=namespace)

            cron_schedule = cronjob.spec.schedule

            return {'success': True, 'data': cron_schedule}

        except Exception as e:
            self.print_ls.error(f"Error get cronjob '{job_name}': {e}")
            return {'success': False, 'data': None}

    @handle_exceptions_async_method
    @trace_k8s_async_method(description="create cloud credentials")
    async def create_cloud_credentials_secret(self, secret_name: str, secret_key: str, aws_access_key_id: str,
                                              aws_secret_access_key: str):
        namespace = self.config_app.get_k8s_velero_namespace()

        # Base64 content encode
        credentials_content = f"""
[default]
aws_access_key_id={aws_access_key_id}
aws_secret_access_key={aws_secret_access_key}
"""
        credentials_base64 = base64.b64encode(credentials_content.encode("utf-8")).decode("utf-8")

        # Create Secret
        secret = client.V1Secret(metadata=client.V1ObjectMeta(name=secret_name, namespace=namespace),
                                 data={f"""{secret_key}""": credentials_base64}, type="Opaque")

        # API client 4 Secrets
        api_instance = client.CoreV1Api()

        try:
            # Create Secret
            api_instance.create_namespaced_secret(namespace=namespace, body=secret)
            print(f"Secret '{secret_name}' create in '{namespace}' namespace.")
            return {'success': True}

        except client.exceptions.ApiException as e:
            return {'success': False, 'error': {'Title': 'create cloud credentials',
                                                'description': f"Exception when create cloud credentials: {e}"}}

    @handle_exceptions_async_method
    @trace_k8s_async_method(description="get velero secret")
    async def get_velero_secret(self):
        try:
            secrets = client.CoreV1Api().list_namespaced_secret(self.config_app.get_k8s_velero_namespace())
            return {'success': True, 'data': [secret.metadata.name for secret in secrets.items]}
        except Exception as e:
            print(f"Can't get secret: {e}")
            return {'success': False, 'error': {'title': "Error", "description": f"No secret retrieved "}}

    @handle_exceptions_async_method
    @trace_k8s_async_method(description="get velero secret")
    async def get_secret_keys(self, secret_name):
        try:
            secret = client.CoreV1Api().read_namespaced_secret(name=secret_name,
                                                               namespace=self.config_app.get_k8s_velero_namespace())
            if secret.data:
                return {'success': True, 'data': list(secret.data.keys())}
            else:
                return {'success': False, 'data': []}
        except client.exceptions.ApiException as e:
            print(f"Error API Kubernetes: {e}")
            return {'success': False, 'error': {'title': "Error", "description": f"No key retrieved "}}
        except Exception as e:
            print(f"Error durante l'ottenimento delle chiavi del Secret: {e}")
            return {'success': False, 'error': {'title': "Error", "description": f"No key retrieved "}}

    @handle_exceptions_async_method
    @trace_k8s_async_method(description="get velero secret")
    async def delete_volume_snapshot_location(self, location_name):
        try:
            api_instance = client.CustomObjectsApi()

            group = "velero.io"
            version = "v1"
            plural = "volumesnapshotlocations"

            # api call to delete resource
            api_instance.delete_namespaced_custom_object(group=group, version=version,
                                                         namespace=self.config_app.get_k8s_velero_namespace(),
                                                         plural=plural, name=location_name)

            print(
                f"VolumeSnapshotLocation '{location_name}' deleted '"
                f"{self.config_app.get_k8s_velero_namespace()}'.")
            return {'success': True}
        except Exception as e:
            print(f"Error: {str(e)}")
            # raise
            return {'success': False, 'error': {'title': 'error', 'description': str(e)}}

    #
    # Test
    #
    def get_velero_backups(self):
        # import json
        # Carica la configurazione del cluster
        # config.load_kube_config()

        # Crea un'istanza del client API
        api_instance = client.CustomObjectsApi()

        # Namespace in cui Velero sta operando
        namespace = "velero"

        # Ottieni gli oggetti di backup di Velero
        group = "velero.io"
        version = "v1"
        plural = "backups"

        try:
            # Chiamata all'API per ottenere i backup
            backups = api_instance.list_namespaced_custom_object(group, version, namespace, plural)

            # Converti il risultato in JSON
            # backups_json = json.dumps(backups, indent=4)

            return backups

        except client.exceptions.ApiException as e:
            print("Exception when calling CustomObjectsApi->list_namespaced_custom_object: %s\n" % e)
            return None

    async def get_pod_volume_backups(self):
        # import json
        # Carica la configurazione del cluster
        # config.load_kube_config()

        # Crea un'istanza del client API
        api_instance = client.CustomObjectsApi()

        # Namespace in cui Velero sta operando
        namespace = "velero"

        # Ottieni gli oggetti di backup di Velero
        group = "velero.io"
        version = "v1"
        plural = "podvolumebackups"

        try:
            # Chiamata all'API per ottenere i backup
            backups = api_instance.list_namespaced_custom_object(group, version, namespace, plural)

            # Converti il risultato in JSON
            # backups_json = json.dumps(backups, indent=4)

            return {'success': True, 'data': backups}
        except Exception as e:
            print(f"Error: {str(e)}")
            # raise
            return {'success': False, 'error': {'title': 'error', 'description': str(e)}}

    async def get_pod_volume_backup(self, backup_name=None):
        # Crea un'istanza del client API
        api_instance = client.CustomObjectsApi()

        # Namespace in cui Velero sta operando
        namespace = "velero"

        # Gruppo, versione e plural per accedere ai backup di Velero
        group = "velero.io"
        version = "v1"
        plural = "podvolumebackups"

        try:
            # Chiamata all'API per ottenere i backup
            backups = api_instance.list_namespaced_custom_object(group, version, namespace, plural)

            # Filtra gli oggetti in base alla label velero.io/backup-uid
            filtered_items = [
                item for item in backups.get('items', [])
                if item.get('metadata', {}).get('labels', {}).get('velero.io/backup-name') == backup_name
            ] if backup_name else backups.get('items', [])

            # Restituisci solo gli oggetti filtrati
            return {'success': True, 'data': filtered_items}
        except Exception as e:
            print(f"Error: {str(e)}")
            return {'success': False, 'error': {'title': 'error', 'description': str(e)}}

    async def get_resource_manifest(self, resource_type, resource_name):
        # Crea un'istanza del client API
        api_instance = client.CustomObjectsApi()

        # Namespace in cui Velero sta operando
        namespace = "velero"

        # Gruppo, versione e plural per accedere ai backup di Velero
        group = "velero.io"
        version = "v1"
        plural = resource_type

        try:
            # Chiamata all'API per ottenere i backup
            backups = api_instance.list_namespaced_custom_object(group, version, namespace, plural)

            # Filtra gli oggetti in base alla label velero.io/backup-uid
            filtered_items = [
                item for item in backups.get('items', [])
                if item.get('metadata', {}).get('name') == resource_name
            ] if resource_name else backups.get('items', [])

            # Restituisci solo gli oggetti filtrati
            return {'success': True, 'data': filtered_items[0]}
        except Exception as e:
            print(f"Error: {str(e)}")
            return {'success': False, 'error': {'title': 'error', 'description': str(e)}}

import sys
from fastapi import HTTPException
from kubernetes import client
from kubernetes.client import ApiException
from datetime import datetime

from configs.config_boot import config_app
from constants.resources import RESOURCES, ResourcesNames
from constants.velero import VELERO
from utils.k8s_tracer import trace_k8s_async_method

from utils.logger_boot import logger
import re

async def _get_node_list(only_problem=False):
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

    except Exception as Ex:
        return 0, 0, None


@trace_k8s_async_method(description="Get k8s online status")
async def get_k8s_online_service():
    ret = False
    total_nodes = 0
    retr_nodes = 0
    try:
        total_nodes, retr_nodes, nodes = await _get_node_list(only_problem=True)
        if nodes is not None:
            ret = True

    except Exception as Ex:
        ret = False

    output = {'cluster_online': ret, 'nodes': {'total': total_nodes, 'in_error': retr_nodes},

              'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')}
    return output


@trace_k8s_async_method(description="Get k8s namespaces")
async def get_namespaces_service():
    # Get namespaces list
    namespace_list = client.CoreV1Api().list_namespace()
    # Extract namespace list
    namespaces = [namespace.metadata.name for namespace in namespace_list.items]
    return namespaces


@trace_k8s_async_method(description="Get k8s all resources list")
async def get_resources_service():
    logger.info(f"load_resources")
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
            logger.debug(f"Retrieved API groups with success")
        except ApiException as e:
            logger.error(f"Exception when retrieving API groups {str(e)}")
            return valid_resources

        for group in api_groups:
            logger.debug(f"find. apihist  group: {group.name}")
            for version in group.versions:
                group_version = f"{group.name}/{version.version}" if group.name else version.version
                try:
                    logger.debug(f"API group version: {group_version}")
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
                    logger.error(
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
            logger.debug(f"load_resources:{res_list_ordered}")
            return res_list_ordered
        else:
            logger.warning(f"load_load_resources:No load_resources found")
            raise HTTPException(status_code=400, detail="No load_resources found")

    except Exception as Ex:
        logger.error(f"{sys.exc_info()} {str(Ex)}")
        raise HTTPException(status_code=400, detail=f"{str(Ex)}")


@trace_k8s_async_method(description="Get k8s storage classes")
async def get_storage_classes_service():
    storage_classes = {}

    storage_classes_list = client.StorageV1Api().list_storage_class()

    if storage_classes_list is not None:
        for sc in storage_classes_list.items:
            v_class = {'name': sc.metadata.name, 'provisioner': sc.provisioner, 'parameters': sc.parameters, }
            storage_classes[sc.metadata.name] = v_class

        return storage_classes
    else:
        raise HTTPException(status_code=400, detail=f"Error when getting storage classes")


def _kubectl_neat(manifest):
    """
    Removes non-essential information from the Kubernetes manifest
    """
    keys_to_remove = ['managedFields', 'creationTimestamp', 'uid', 'resourceVersion']

    def clean_dict(d):
        if isinstance(d, dict):
            return {k: clean_dict(v) for k, v in d.items() if k not in keys_to_remove}
        elif isinstance(d, list):
            return [clean_dict(i) for i in d]
        return d

    return clean_dict(manifest)

def _to_snake_case(phrase):
    return re.sub(r'(?<!^)(?=[A-Z])', '_', phrase).upper()

@trace_k8s_async_method(description="Get resource manifest")
async def get_velero_resource_manifest_service(resource_type: str, resource_name: str, neat=False):
    # Create an instance of the API client
    api_instance = client.CustomObjectsApi()

    # Namespace in which Velero is operating
    namespace = config_app.k8s.velero_namespace
    # Group, version and plural to access Velero backups
    group = VELERO['GROUP']
    version = VELERO['VERSION']
    plural = RESOURCES[ResourcesNames[_to_snake_case(resource_type)]].plural

    try:
        # API call to get backups
        backups = api_instance.list_namespaced_custom_object(group, version, namespace, plural)

        # Filter objects by label velero.io/backup-uid
        filtered_items = [
            item for item in backups.get('items', [])
            if item.get('metadata', {}).get('name') == resource_name
        ] if resource_name else backups.get('items', [])

        # Return only filtered objects
        manifest = filtered_items[0]

        if neat:
            return _kubectl_neat(manifest)
        return manifest
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=404, detail=f"{str(e)}")

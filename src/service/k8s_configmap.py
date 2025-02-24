from fastapi import HTTPException
from kubernetes import client
from kubernetes.client import ApiException

from utils.k8s_tracer import trace_k8s_async_method
from utils.logger_boot import logger


@trace_k8s_async_method(description="Get configmap")
async def get_config_map_service(namespace, configmap_name):
    # Kubernetes API client
    core_api = client.CoreV1Api()

    try:
        # Retrieve the ConfigMap
        configmap = core_api.read_namespaced_config_map(name=configmap_name, namespace=namespace)

        # Access the data in the ConfigMap
        data = configmap.data
        if not data:
            raise HTTPException(status_code=400, detail=f"Error get config map service")
        kv = {}
        # Print out the data
        for key, value in data.items():
            if (key.startswith('SECURITY_TOKEN_KEY') or key.startswith('EMAIL_PASSWORD') or
                    key.startswith('TELEGRAM_TOKEN')):
                value = value[0].ljust(len(value) - 1, '*')
            kv[key] = value
        return kv
    except client.exceptions.ApiException as e:
        logger.warning(f"Exception when calling CoreV1Api->read_namespaced_config_map: {e}")
        # raise HTTPException(status_code=400, detail=f"Exception when calling "
        #                                             f"CoreV1Api->read_namespaced_config_map: {e}")
        return None


@trace_k8s_async_method(description="Create or update a configmap")
async def create_or_update_configmap_service(namespace, configmap_name, key, value):
    """
     Create or update a ConfigMap in Kubernetes.

    Args:
        namespace (str): The namespace of the ConfigMap.
        configmap_name (str): The name of the ConfigMap.
        key (str): The key to be updated.
        value (str): The value to be assigned to the key.

    Returns:
        dict: The updated or created ConfigMap.
    """

    v1 = client.CoreV1Api()

    try:
        # Try retrieving the existing ConfigMap
        existing_configmap = v1.read_namespaced_config_map(name=configmap_name, namespace=namespace)
        print(f"ConfigMap '{configmap_name}' found, update in progress...")

        # Update the value of the key
        if existing_configmap.data is None:
            existing_configmap.data = {}

        existing_configmap.data[key] = value
        updated_configmap = v1.replace_namespaced_config_map(name=configmap_name, namespace=namespace,
                                                             body=existing_configmap)
        print(f"ConfigMap '{configmap_name}' updated with {key}: {value}")

    except ApiException as e:
        if e.status == 404:
            print(f"ConfigMap '{configmap_name}' not found, creation in progress...")

            # Creating the ConfigMap
            configmap = client.V1ConfigMap(
                metadata=client.V1ObjectMeta(name=configmap_name),
                data={key: value}
            )

            created_configmap = v1.create_namespaced_config_map(namespace=namespace, body=configmap)
            print(f"ConfigMap '{configmap_name}' created with {key}: {value}")
            return created_configmap
        else:
            print(f"Error while accessing ConfigMap: {e}")
            return None

    return updated_configmap


@trace_k8s_async_method(description="Remove a key from configmap")
async def remove_key_from_configmap_service(namespace, configmap_name, key):
    """
    Removes a key from a ConfigMap in Kubernetes.

    Args:
        namespace (str): The namespace of the ConfigMap.
        configmap_name (str): The name of the ConfigMap.
        key (str): The key to be removed.

    Returns:
        dict | None: The updated ConfigMap or None if the ConfigMap has been deleted or does not exist.
    """

    v1 = client.CoreV1Api()

    try:
        # Retrieve the ConfigMap
        configmap = v1.read_namespaced_config_map(name=configmap_name, namespace=namespace)

        # Check if the key exists
        if configmap.data is None or key not in configmap.data:
            print(f"The key '{key}' does not exist in the ConfigMap '{configmap_name}'.")
            return configmap

        # Removes the specified key
        del configmap.data[key]
        print(f"Key '{key}' removed from ConfigMap '{configmap_name}'.")

        # If the ConfigMap is empty, you can choose to delete it
        # if not configmap.data:  # If there are no more keys
        #     print(f"The ConfigMap '{configmap_name}' is empty. Deleting it...")
        #     v1.delete_namespaced_config_map(name=configmap_name, namespace=namespace)
        #     return None  # Indicates that the ConfigMap has been deleted

        # Otherwise, update the ConfigMap
        updated_configmap = v1.replace_namespaced_config_map(name=configmap_name, namespace=namespace,
                                                             body=configmap)
        return updated_configmap

    except ApiException as e:
        if e.status == 404:
            print(f"ConfigMap '{configmap_name}' not found in namespace '{namespace}'.")
        else:
            print(f"Error while accessing ConfigMap: {e}")
        return None


@trace_k8s_async_method(description="Create apparise user configmap")
async def create_configmap_service(namespace, configmap_name, data):
    """
    Create a ConfigMap in Kubernetes.

    Args:
        namespace (str): The namespace of the ConfigMap.
        configmap_name (str): The name of the ConfigMap.
        data (dict): A dictionary with the keys and values to be included in the ConfigMap.

    Returns:
        dict: The ConfigMap created, or None if it already exists.
    """

    v1 = client.CoreV1Api()

    # Defines the ConfigMap
    configmap = client.V1ConfigMap(
        metadata=client.V1ObjectMeta(name=configmap_name),
        data=data
    )

    try:
        # Check if the ConfigMap already exists
        v1.read_namespaced_config_map(name=configmap_name, namespace=namespace)
        print(f"The ConfigMap '{configmap_name}' already exists in the namespace '{namespace}'.")
        return None  # Does not create a new ConfigMap if it already exists

    except ApiException as e:
        if e.status == 404:
            # If the ConfigMap does not exist, it creates it
            created_configmap = v1.create_namespaced_config_map(namespace=namespace, body=configmap)
            print(f"ConfigMap '{configmap_name}' successfully created in the namespace '{namespace}'.")
            return created_configmap
        else:
            print(f"Error while creating the ConfigMap: {e}")
            return None

import base64

from fastapi import HTTPException
from kubernetes import client
from kubernetes.client import ApiException

from vui_common.configs.config_proxy import config_app
from vui_common.utils.k8s_tracer import trace_k8s_async_method


@trace_k8s_async_method(description="Get velero secret list names")
async def get_velero_secret_service():
    try:
        secrets = client.CoreV1Api().list_namespaced_secret(config_app.k8s.velero_namespace)
        return [secret.metadata.name for secret in secrets.items]
    except Exception as e:
        print(f"Can't get secret: {e}")
        raise HTTPException(status_code=400, detail=f"No secret retrieved")


@trace_k8s_async_method(description="Get secret's keys")
async def get_secret_keys_service(namespace: str, secret_name: str):
    try:
        secret = client.CoreV1Api().read_namespaced_secret(name=secret_name,
                                                           namespace=namespace)
        if secret.data:
            return list(secret.data.keys())
        else:
            return []
    except client.exceptions.ApiException as e:
        print(f"Error API Kubernetes: {e}")
        raise HTTPException(status_code=400, detail=f"Error API Kubernetes: {e}")
    except Exception as e:
        print(f"Error while obtaining Secret keys: {e}")
        raise HTTPException(status_code=400, detail=f"Error while obtaining Secret keys: {e}")


@trace_k8s_async_method(description="get secret content")
async def get_secret_service(namespace: str, secret_name: str):
    try:
        secret = client.CoreV1Api().read_namespaced_secret(name=secret_name,
                                                           namespace=namespace)
        if secret.data:
            decoded_data = {key: base64.b64decode(value).decode('utf-8') for key, value in secret.data.items()}
            return decoded_data
        else:
            return []
    except client.exceptions.ApiException as e:
        print(f"Error API Kubernetes: {e}")
        # raise HTTPException(status_code=400, detail=f"Error API Kubernetes: {e}")
        return None

    except Exception as e:
        print(f"Error while obtaining Secret keys: {e}")
        # raise HTTPException(status_code=400, detail=f"Error while obtaining Secret keys: {e}")
        return None


@trace_k8s_async_method(description="add or update key:value in secret")
async def add_or_update_key_in_secret_service(namespace, secret_name, key, value):
    """
    Adds or updates a key in a Secret Kubernetes.

    Args:
        namespace (str): The namespace of the Secret.
        secret_name (str): The name of the Secret.
        key (str): The key to be added or updated.
        value (str): The value of the key (not base64 encoded).

    Returns:
        dict | None: The updated Secret, or None in case of an error
    """
    # Upload Kubernetes configuration
    # config.load_kube_config()

    v1 = client.CoreV1Api()

    try:
        secret = v1.read_namespaced_secret(name=secret_name, namespace=namespace)

        if secret.data is None:
            secret.data = {}

        # Encode value in base64
        secret.data[key] = base64.b64encode(value.encode()).decode()

        updated_secret = v1.replace_namespaced_secret(name=secret_name, namespace=namespace, body=secret)
        print(f"Key '{key}' added/updated in Secret '{secret_name}'.")
        return updated_secret

    except ApiException as e:
        if e.status == 404:
            print(f"Secret '{secret_name}' not found in namespace '{namespace}'. Create it before adding key")
            # Create the Secret with the key and the value
            secret_data = {key: base64.b64encode(value.encode()).decode()}
            new_secret = client.V1Secret(
                metadata=client.V1ObjectMeta(name=secret_name),
                data=secret_data,
                type="Opaque"
            )

            created_secret = v1.create_namespaced_secret(namespace=namespace, body=new_secret)
            print(f"Secret '{secret_name}' created with key '{key}'.")
            return created_secret
        else:
            print(f"Error when updating Secret: {e}")
        return None


@trace_k8s_async_method(description="remove key from secret")
def remove_key_from_secret_service(namespace, secret_name, key):
    """
    Removes a key from a Secret Kubernetes.

    Args:
        namespace (str): The namespace of the Secret.
        secret_name (str): The name of the Secret.
        key (str): The key to be removed.

    Returns:
        dict | None: The updated Secret or None if the Secret has been deleted or does not exist.
    """
    # Upload Kubernetes configuration
    # config.load_kube_config()

    v1 = client.CoreV1Api()

    try:
        secret = v1.read_namespaced_secret(name=secret_name, namespace=namespace)

        if secret.data is None or key not in secret.data:
            print(f"The key '{key}' does not exist in Secret '{secret_name}'.")
            return secret

        # Removes the key
        del secret.data[key]
        print(f"Key '{key}' removed from Secret '{secret_name}'.")

        # If Secret is empty, it deletes it
        if not secret.data:
            print(f"The Secret '{secret_name}' is now empty. Deleting it...")
            v1.delete_namespaced_secret(name=secret_name, namespace=namespace)
            return None

        updated_secret = v1.replace_namespaced_secret(name=secret_name, namespace=namespace, body=secret)
        return updated_secret

    except ApiException as e:
        if e.status == 404:
            print(f"Secret '{secret_name}' not found in namespace '{namespace}'.")
        else:
            print(f"Error while accessing Secret: {e}")
        return None

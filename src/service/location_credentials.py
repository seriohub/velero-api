import base64
import configparser
import os

from fastapi import HTTPException
from kubernetes import client

from vui_common.configs.config_proxy import config_app
from vui_common.utils.k8s_tracer import trace_k8s_async_method


@trace_k8s_async_method(description="get s3 credential")
async def get_credential_service(secret_name, secret_key):
    api_instance = client.CoreV1Api()

    # LS 2024.20.22 use env variable
    # secret = api_instance.read_namespaced_secret(name=secret_name, namespace='velero')
    secret = api_instance.read_namespaced_secret(name=secret_name,
                                                 namespace=os.getenv('K8S_VELERO_NAMESPACE', 'velero'))
    if secret.data and secret_key in secret.data:
        value = secret.data[secret_key]
        decoded_value = base64.b64decode(value)
        payload = _parse_config_string(decoded_value.decode('utf-8'))
        return payload
    else:
        raise HTTPException(status_code=400, detail=f"Secret key not found")


@trace_k8s_async_method(description="get default s3 credential")
async def get_default_credential_service():
    label_selector = 'app.kubernetes.io/name=velero'
    api_instance = client.CoreV1Api()

    secret = api_instance.list_namespaced_secret(namespace=os.getenv('K8S_VELERO_NAMESPACE', 'velero'),
                                                 label_selector=label_selector)

    if secret.items[0].data:
        value = secret.items[0].data['cloud']
        decoded_value = base64.b64decode(value)

        payload = _parse_config_string(decoded_value.decode('utf-8'))

        return payload
    else:
        raise HTTPException(status_code=400, detail=f"Secret key not found")


@trace_k8s_async_method(description="create cloud credentials")
async def create_cloud_credentials_secret_service(secret_name: str, secret_key: str, aws_access_key_id: str,
                                                  aws_secret_access_key: str):
    namespace = config_app.k8s.velero_namespace

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
        return True

    except client.exceptions.ApiException as e:
        raise HTTPException(status_code=400, detail=f"Exception when create cloud credentials: {e}")


def _parse_config_string(config_string):
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

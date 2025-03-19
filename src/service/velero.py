import re

from kubernetes import client
from kubernetes.client import ApiException

from configs.config_boot import config_app
from utils.k8s_tracer import trace_k8s_async_method

coreV1 = client.CoreV1Api()


def _parse_version_output(output):
    # Initialize the result dictionary
    result = {'client': {}, 'server': {}, 'warning': None}

    # Find client information
    client_match = re.search(r'Client:\n\tVersion:\s+(?P<version>[\w.-]+)\n\tGit commit:\s+(?P<git_commit>\w+)',
                             output)
    if client_match:
        result['client']['version'] = client_match.group('version')
        result['client']['GitCommit'] = client_match.group('git_commit')

    # Finds server information
    server_match = re.search(r'Server:\n\tVersion:\s+(?P<version>[\w.-]+)', output)
    if server_match:
        result['server']['version'] = server_match.group('version')

    # Finds warning, if any
    warning_match = re.search(r'# WARNING:\s+(?P<warning>.+)', output)
    if warning_match:
        result['warning'] = warning_match.group('warning')

    return result


@trace_k8s_async_method(description="Get velero Version")
async def get_velero_version_service():
    namespace = config_app.k8s.velero_namespace
    label_selectors = [
        "name=velero",
        "app.kubernetes.io/name=velero",
        "component=velero",
        "k8s-app=velero"
    ]

    try:
        for label_selector in label_selectors:
            pods = coreV1.list_namespaced_pod(namespace=namespace, label_selector=label_selector)

            if pods.items:
                pod = pods.items[0]
                container_image = pod.spec.containers[0].image

                if ':' in container_image:
                    _, version = container_image.split(':')
                    return version
                else:
                    print("Unable to determine version from container image.")
                    return None

        print("No pods found with any of the specified labels.")
        return None

    except ApiException as e:
        print(f"Error while accessing pods: {e}")
        return None

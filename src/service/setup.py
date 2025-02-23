import re

from kubernetes import client
from kubernetes.client import ApiException

from configs.config_boot import config_app


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


async def get_velero_version_service():
    namespace = config_app.get_k8s_velero_namespace()
    label_selector = "app.kubernetes.io/name=velero"

    try:
        pods = coreV1.list_namespaced_pod(namespace=namespace, label_selector=label_selector)

        if not pods.items:
            print("No pods found with the specified label.")
            return None

        pod = pods.items[0]

        container_image = pod.spec.containers[0].image

        if ':' in container_image:
            _, version = container_image.split(':')
            return version
        else:
            print("Unable to determine version from container image.")
            return None

    except ApiException as e:
        print(f"Errore durante l'accesso ai pod: {e}")
        return None

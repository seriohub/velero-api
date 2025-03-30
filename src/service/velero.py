import re
import asyncio
from kubernetes import client
from kubernetes.client import ApiException

from configs.config_boot import config_app
from utils.k8s_tracer import trace_k8s_async_method
from configs.config_boot import config_app
from datetime import timezone

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


@trace_k8s_async_method(description="Get velero Pods")
async def get_pods_service(label_selectors_by_type, namespace):
    coreV1 = client.CoreV1Api()

    pods_info = []
    seen_pods = set()

    # label_selectors_by_type = {
    #     "velero": "name=velero",
    #     "node-agent": "name=node-agent"
    # }

    for pod_type, label_selector in label_selectors_by_type.items():
        try:
            pods = coreV1.list_namespaced_pod(namespace=namespace, label_selector=label_selector)
            for pod in pods.items:
                pod_name = pod.metadata.name
                if pod_name in seen_pods:
                    continue

                seen_pods.add(pod_name)

                # Info generali
                image = pod.spec.containers[0].image if pod.spec.containers else "unknown"
                version = image.split(":")[-1] if ":" in image else "unknown"
                status = pod.status.phase
                restarts = sum(c.restart_count for c in pod.status.container_statuses or [])
                created = pod.metadata.creation_timestamp.astimezone(
                    timezone.utc).isoformat() if pod.metadata.creation_timestamp else "unknown"

                pods_info.append({
                    "podName": pod_name,
                    "type": pod_type,
                    "nodeName": pod.spec.node_name,
                    "ip": pod.status.pod_ip,
                    "status": status,
                    "restarts": restarts,
                    "created": created,
                    "version": version,
                })

        except client.exceptions.ApiException as e:
            print(f"Errore durante la richiesta con selector '{label_selector}': {e}")

    return pods_info


async def get_pod_logs_service(pod, namespace="velero", lines=100):
    coreV1 = client.CoreV1Api()

    def _get_logs():
        try:
            return coreV1.read_namespaced_pod_log(
                name=pod,
                namespace=namespace,
                tail_lines=lines,
                timestamps=False,
            )
        except client.exceptions.ApiException as e:
            return f"error while fetching logs for '{pod}': {e}"

    logs = (await asyncio.to_thread(_get_logs)).split("\n")
    return logs

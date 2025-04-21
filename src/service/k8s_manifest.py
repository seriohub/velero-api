import re
from datetime import datetime

from fastapi import HTTPException
from kubernetes import client
from kubernetes.client import ApiException

from constants.k8s import K8S_PLURALS
from service.k8s import _kubectl_neat
from vui_common.utils.k8s_tracer import trace_k8s_async_method


@trace_k8s_async_method(description="Get resource manifest")
async def get_k8s_resource_manifest_service(kind: str,
                                            name: str,
                                            namespace: str = None,
                                            api_version: str = "v1",
                                            is_cluster_resource: bool = False,
                                            neat=False):
    """
    Gets the manifest of a Kubernetes resource, including Custom Resources (CRDs).

    :param kind: Type of the resource (e.g., “pods,” “deployments,” “backupstoragelocations”).
    :param name: Name of the resource.
    :param namespace: Namespace of the resource (None for cluster-wide resources).
    :param api_version: API Version of the resource (ex: “apps/v1”, “batch/v1”, “velero.io/v1”).
    :param is_cluster_resource: True if the resource is cluster-wide (ex: Nodes, StorageClasses).
    :param neat: If True, returns the manifest without superfluous metadata.
    :return: The manifest of the resource as a dictionary.
    """

    api_client = client.ApiClient()

    try:
        # CRD management (if apiVersion contains “/”)
        if "/" in api_version:
            group, version = api_version.split("/")
            plural = _get_plural_from_crd(kind=kind, api_version=api_version)
            if not plural:
                raise HTTPException(status_code=400,
                                    detail=f"For Custom Resources (CRD), the parameter 'plural' is mandatory")

            api_instance = client.CustomObjectsApi(api_client)

            if is_cluster_resource:
                response = api_instance.get_cluster_custom_object(
                    group=group,
                    version=version,
                    plural=plural,
                    name=name
                )
            else:
                response = api_instance.get_namespaced_custom_object(
                    group=group,
                    version=version,
                    namespace=namespace,
                    plural=plural,
                    name=name
                )

        else:
            kind = K8S_PLURALS[kind]
            # API Clients
            core_api_instance = client.CoreV1Api()
            app_api_instance = client.AppsV1Api()
            batch_api_instance = client.BatchV1Api()
            storage_api_instance = client.StorageV1Api()

            # Core API group (`v1`)
            core_resources = {
                "pods": core_api_instance.read_namespaced_pod,
                "services": core_api_instance.read_namespaced_service,
                "configmaps": core_api_instance.read_namespaced_config_map,
                "secrets": core_api_instance.read_namespaced_secret,
                "endpoints": core_api_instance.read_namespaced_endpoints,
                "persistentvolumeclaims": core_api_instance.read_namespaced_persistent_volume_claim,
                "events": core_api_instance.read_namespaced_event,
                "serviceaccounts": core_api_instance.read_namespaced_service_account,
            }

            # Apps API group (`apps/v1`)
            apps_resources = {
                "deployments": app_api_instance.read_namespaced_deployment,
                "statefulsets": app_api_instance.read_namespaced_stateful_set,
                "daemonsets": app_api_instance.read_namespaced_daemon_set,
            }

            # Batch API group (`batch/v1`)
            batch_resources = {
                "jobs": batch_api_instance.read_namespaced_job,
                "cronjobs": batch_api_instance.read_namespaced_cron_job,
            }

            # Cluster-wide resources
            cluster_resources = {
                "nodes": core_api_instance.read_node,
                "storageclasses": storage_api_instance.read_storage_class,
                "namespaces": core_api_instance.read_namespace
            }

            # Check API core (`v1`)
            if api_version == "v1":
                if kind in core_resources:
                    response = core_resources[kind](name=name, namespace=namespace).to_dict()
                elif is_cluster_resource and kind in cluster_resources:
                    response = cluster_resources[kind](name=name).to_dict()
                else:
                    raise HTTPException(status_code=400,
                                        detail=f"Resource '{kind}' not found in core API group ('v1')")

            # Check `apps/v1`
            elif api_version == "apps/v1":
                if kind in apps_resources:
                    response = apps_resources[kind](name=name, namespace=namespace).to_dict()
                else:
                    raise HTTPException(status_code=400,
                                        detail=f"Resource '{kind}' not found in 'apps/v1'")

            # Check `batch/v1`
            elif api_version == "batch/v1":
                if kind in batch_resources:
                    response = batch_resources[kind](name=name, namespace=namespace).to_dict()
                else:
                    raise HTTPException(status_code=400,
                                        detail=f"Resource '{kind}' not found in 'batch/v1'")

            else:
                raise HTTPException(status_code=400,
                                    detail=f"API Version '{api_version}' not supported for resource '{kind}'.")

        # Clean manifest if needed
        if neat:
            response = _kubectl_neat(response)

        # Convert datetime to serializable JSON strings
        response = _convert_datetime(response)
        response = _convert_keys_to_camel_case(response)
        return response

    except ApiException as e:
        raise HTTPException(status_code=400,
                            detail=f"Errore API: {e.status} - {e.reason}\n{e.body}")


def _convert_datetime(obj):
    """
    Converts all datetime type values to ISO 8601 strings recursively.
    """
    if isinstance(obj, dict):
        return {k: _convert_datetime(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_convert_datetime(v) for v in obj]
    elif isinstance(obj, datetime):
        return obj.isoformat()
    else:
        return obj


def _get_plural_from_crd(kind: str, api_version: str):
    """
    Gets the plural name of a Kubernetes resource.
    If it is a standard resource, it uses the K8S_PLURALS dictionary.
    If it is a CRD, it looks it up in the CustomResourceDefinitions.

    :param kind: Kind name of the resource (e.g., “Backup,” “Deployment”).
    :param api_version: API Group and Version (ex: “velero.io/v1”, “apps/v1”).
    :return: Plural name of the resource (ex: “backups”, “deployments”).
    """
    # If the resource is native to Kubernetes, return the already known plural
    if kind in K8S_PLURALS:
        return K8S_PLURALS[kind]

    api_client = client.ApiClient()
    crd_api = client.ApiextensionsV1Api(api_client)

    group, version = api_version.split("/")
    crds = crd_api.list_custom_resource_definition()

    for crd in crds.items:
        # print(kind, crd.spec.group, crd.spec.names.kind.lower(), crd.spec.names.plural )
        if crd.spec.group == group and crd.spec.names.kind.lower() == kind.lower():
            return crd.spec.names.plural  # ✅ Nome corretto del plural per CRD

    raise HTTPException(status_code=400, detail=f"Plural not found for Kind '{kind}' in API '{api_version}'")


def _convert_keys_to_camel_case(obj):
    """
    Converts keys in a dictionary from snake_case to camelCase recursively.
    """
    if isinstance(obj, dict):
        new_obj = {}
        for k, v in obj.items():
            camel_key = re.sub(r'_([a-z])', lambda x: x.group(1).upper(), k)
            new_obj[camel_key] = _convert_keys_to_camel_case(v)
        return new_obj
    elif isinstance(obj, list):
        return [_convert_keys_to_camel_case(v) for v in obj]
    else:
        return obj

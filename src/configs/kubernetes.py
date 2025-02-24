import os


class KubernetesConfig:
    def __init__(self):
        self.velero_namespace = os.getenv('K8S_VELERO_NAMESPACE', 'velero')
        self.in_cluster_mode = os.getenv('K8S_IN_CLUSTER_MODE', 'False').lower() == 'true'
        self.kube_config = os.getenv('KUBE_CONFIG_FILE', '')
        self.cluster_id = os.getenv('CLUSTER_ID', 'not-defined')
        self.vui_namespace = os.getenv('K8S_VELERO_UI_NAMESPACE', 'velero')

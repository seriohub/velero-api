# app_data.py
import os
from core.config import ConfigHelper
from service.k8s_service import K8sService
import asyncio

config_app = ConfigHelper()
k8sService = K8sService()
env = config_app.get_env_variables()

if os.getenv('K8S_IN_CLUSTER_MODE').lower() == 'true':
    env_data = asyncio.run(k8sService.get_config_map(namespace=config_app.get_k8s_velero_ui_namespace(), configmap_name='velero-api-config'))
else:
    env_data = config_app.get_env_variables()

__version__ = config_app.get_build_version()
__date__ = config_app.get_date_build()
__app_name__ = 'velero-api'
__app_summary__ = 'A lightweight framework for managing your velero operations.'
__admin_email__ = config_app.get_admin_email()
__app_description__ = "<br>".join("{}: <b>{}</b>".format(k, v) for k, v in env.items())

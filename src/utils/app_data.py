# app_data.py
from libs.config import ConfigEnv
config_app = ConfigEnv()

__version__ = config_app.get_build_version()
__date__ = config_app.get_date_build()
__app_name__ = 'velero-api'
__app_summary__ = 'A lightweight framework for managing your velero operations'
__admin_email__ = config_app.get_admin_email()
__app_description__ = 'Supports velero-UI for handling and monitoring the status and the operations'


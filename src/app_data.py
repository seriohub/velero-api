from core.config import ConfigHelper

config_app = ConfigHelper()

__version__ = config_app.get_build_version()
__date__ = config_app.get_date_build()
__app_name__ = 'velero-api'
__app_summary__ = 'Velero-API is part of the VUI project'
__admin_email__ = config_app.get_admin_email()
# __app_description__ = "<br>".join("{}: <b>{}</b>".format(k, v) for k, v in env.items())
__app_description__ = ''
__helm_version__ = config_app.get_helm_version()
__helm_app_version__ = config_app.get_helm_app_version()
__helm_api__ = config_app.get_helm_api()
__helm_ui__ = config_app.get_helm_ui()
__helm_watchdog__ = config_app.get_helm_watchdog()

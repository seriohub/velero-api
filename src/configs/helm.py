import os


class HelmConfig:
    def __init__(self):
        self.version = os.getenv('HELM_VERSION', '-')
        self.app_version = os.getenv('HELM_APP_VERSION', '-')
        self.api = os.getenv('HELM_API', '-')
        self.ui = os.getenv('HELM_UI', '-')
        self.watchdog = os.getenv('HELM_WATCHDOG', '-')

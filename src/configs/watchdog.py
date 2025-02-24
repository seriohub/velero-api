import os

class WatchdogConfig:
    def __init__(self):
        self.url = self._get_watchdog_url()
        self.report_cronjob_name = os.getenv('WATCHDOG_REPORT_CRONJOB_NAME', 'vui-report')

    @staticmethod
    def _get_watchdog_url():
        """Determines the Watchdog URL based on K8s mode."""
        if os.getenv('K8S_IN_CLUSTER_MODE', 'False').lower() == 'true':
            watchdog_url = os.getenv('WATCHDOG_URL', '').strip()
            watchdog_port = os.getenv('WATCHDOG_PORT', '').strip()
            return f"{watchdog_url}:{watchdog_port}" if watchdog_url and watchdog_port else '127.0.0.1:8002'
        return '127.0.0.1:8002'

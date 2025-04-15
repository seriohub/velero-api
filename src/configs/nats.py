import os


class NATSConfig:
    def __init__(self):
        self.enable = os.getenv('NATS_ENABLE', 'false').lower() == 'true'
        self.protocol = os.getenv('NATS_PROTOCOL', 'nats')
        self.endpoint_url = os.getenv('NATS_ENDPOINT_URL', '127.0.0.1')
        self.client_port = int(os.getenv('NATS_PORT_CLIENT', '4222'))
        self.monitoring_port = int(os.getenv('NATS_PORT_MONITORING', '8222'))
        self.username = os.getenv('NATS_USERNAME', None)
        self.password = os.getenv('NATS_PASSWORD', None)

        self.retry_connection = int(os.getenv('NATS_RETRY_CONN_SEC', '20'))
        self.retry_registration = int(os.getenv('NATS_RETRY_REG_SEC', '30'))
        self.send_alive = int(os.getenv('NATS_ALIVE_SEC', '60'))
        self.timeout_request = int(os.getenv('NATS_REQUEST_TIMEOUT_SEC', '2'))

        self.cron_k8s_health_update = int(os.getenv('NATS_CRON_UPDATE_K8S_HEALTH', '300'))
        self.cron_get_stats_update = int(os.getenv('NATS_CRON_UPDATE_STATS_GET', '300'))
        self.cron_backup_update = int(os.getenv('NATS_CRON_UPDATE_BACKUP', '300'))
        self.cron_restore_update = int(os.getenv('NATS_CRON_UPDATE_RESTORE', '300'))
        self.cron_schedules_update = int(os.getenv('NATS_CRON_UPDATE_SCHEDULES', '300'))
        self.cron_backup_location_update = int(os.getenv('NATS_CRON_UPDATE_BACKUP_LOCATION', '300'))
        self.cron_locations_update = int(os.getenv('NATS_CRON_UPDATE_STORAGE_LOCATION', '300'))
        self.cron_repository_update = int(os.getenv('NATS_CRON_UPDATE_REPOSITORIES', '300'))
        self.cron_storage_classes_mapping_update = int(os.getenv('NATS_CRON_UPDATE_SC_MAPPING', '300'))

        self.nats_client_url = f"{self.protocol}://{self.username}:{self.password}@{self.endpoint_url}:{self.client_port}"

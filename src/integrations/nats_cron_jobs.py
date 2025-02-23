from configs.config_boot import config_app
from integrations.nats_cron_job import NatsCronJob







class NatsCronJobs:
    def __init__(self):
        self.jobs = {}
        self.__init_default_api()

    def __init_default_api(self):
        # logger.debug(f"__init_default_api")
        self.add_job(endpoint="/v1/stats",
                     credential=True,
                     interval=config_app.get_nats_cron_update_sec_statistic())

        self.add_job(endpoint="/health/k8s",
                     credential=False,
                     interval=config_app.get_nats_cron_update_sec_statistic())

        self.add_job(endpoint="/v1/backups",
                     credential=True,
                     interval=config_app.get_nats_cron_update_sec_backup())

        self.add_job(endpoint="/v1/restores",
                     credential=True,
                     interval=config_app.get_nats_cron_update_sec_restore())

        self.add_job(endpoint="/v1/schedules",
                     credential=True,
                     interval=config_app.get_nats_cron_update_sec_schedules())

        self.add_job(endpoint="/v1/bsl",
                     credential=True,
                     interval=config_app.get_nats_cron_update_sec_backup_location())

        self.add_job(endpoint="/v1/vsl",
                     credential=True,
                     interval=config_app.get_nats_cron_update_sec_storage_location())

        self.add_job(endpoint="/v1/repos",
                     credential=True,
                     interval=config_app.get_nats_cron_update_sec_repositories())

        self.add_job(endpoint="/v1/sc-mapping",
                     credential=True,
                     interval=config_app.get_nats_cron_update_sec_sc_mapping())

    def add_job(self, endpoint: str, credential: bool, interval: int):
        if len(endpoint) and interval > 0:
            jobs = NatsCronJob(endpoint=endpoint,
                               credential_required=credential,
                               interval=interval)
            self.jobs[jobs.endpoint] = jobs
            logger.debug(f"add_job. jobs added with success, endpoint:{endpoint}")
            return True
        else:
            logger.warning(f"add_job. parameters are invalid. "
                           f"endpoint:{endpoint} interval:{interval}")
            return False

    def get_jobs(self, name: str):
        if name in self.jobs:
            return self.jobs[name]
        else:
            raise KeyError(f"No timer found with the name: {name}")

    def add_tick_to_interval(self, interval: int):
        # self.print_ls.debug(f"add_tick_to_interval")
        for key, job in self.jobs.items():
            job.time_elapsed = interval

    def print_info(self):
        # self.print_ls.debug(f"add_tick_to_interval")
        if not self.jobs:
            logger.debug(f"add_tick_to_interval. No cron job to display.")
        else:
            for name, job in self.jobs.items():
                logger.debug(f"api: {job.endpoint} "
                             f"interval sec: {job.interval} "
                             f"key: {job.ky_key} ")

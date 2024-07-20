from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict
import json

from core.config import ConfigHelper
from helpers.nats_cron_job import NatsCronJob
from helpers.printer import PrintHelper

config = ConfigHelper()


class NatsCronJobs:
    def __init__(self):
        self.print_ls = PrintHelper('[helpers.nats.cron.jobs]',
                                    level=config.get_internal_log_level())
        self.jobs = {}
        self.__init_default_api()

    def __init_default_api(self):
        self.print_ls.debug(f"__init_default_api")
        self.add_job(endpoint="/api/v1/stats/get",
                     credential=True,
                     interval=config.get_nats_cron_update_sec_statistic())

        self.add_job(endpoint="/api/info/health-k8s",
                     credential=False,
                     interval=config.get_nats_cron_update_sec_statistic())

        self.add_job(endpoint="/api/v1/backup/get",
                     credential=True,
                     interval=config.get_nats_cron_update_sec_backup())
c
        self.add_job(endpoint="/api/v1/restore/get",
                     credential=True,
                     interval=config.get_nats_cron_update_sec_restore())

        self.add_job(endpoint="/api/v1/schedule/get",
                     credential=True,
                     interval=config.get_nats_cron_update_sec_schedules())

        self.add_job(endpoint="/api/v1/backup-location/get",
                     credential=True,
                     interval=config.get_nats_cron_update_sec_backup_location())

        self.add_job(endpoint="api/v1/snapshot-location/get",
                     credential=True,
                     interval=config.get_nats_cron_update_sec_storage_location())

        self.add_job(endpoint="/api/v1/repo/get",
                     credential=True,
                     interval=config.get_nats_cron_update_sec_repositories())

        self.add_job(endpoint="/api/v1/sc/change-storage-classes-config-map/get",
                     credential=True,
                     interval=config.get_nats_cron_update_sec_sc_mapping())

    def add_job(self, endpoint: str, credential: bool, interval: int):
        if len(endpoint) and interval > 0:
            jobs = NatsCronJob(endpoint=endpoint,
                               credential_required=credential,
                               interval=interval)
            self.jobs[jobs.endpoint] = jobs
            self.print_ls.debug(f"add_job. jobs added with success")
            return True
        else:
            self.print_ls.wrn(f"add_job. parameters are invalid. "
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
        self.print_ls.debug(f"add_tick_to_interval")
        if not self.jobs:
            self.print_ls.debug(f"add_tick_to_interval. No cron job to display.")
        else:
            for name, job in self.jobs.items():
                self.print_ls.debug(f"api: {job.endpoint} "
                                    f"interval sec: {job.interval} "
                                    f"key: {job.ky_key} ")

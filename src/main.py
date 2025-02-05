# import os

import uvicorn
import asyncio
from multiprocessing import Process
import time

from app_data import __version__, __app_name__

from security.helpers.database import SessionLocal
from security.service.helpers.users import create_default_user

from service.info_service import InfoService

from helpers.velero_client import VeleroClient

from helpers.logger import ColoredLogger, LEVEL_MAPPING
import logging

from core.config import ConfigHelper

import uvicorn_filter

# import sentry_sdk
#
# sentry_sdk.init(
#     dsn="http://b9ec3373cc7ef4345b891b8bc728614d@127.0.0.1:9009/2",
#     # Set traces_sample_rate to 1.0 to capture 100%
#     # of transactions for performance monitoring.
#     traces_sample_rate=1.0,
#     release=os.getenv('BUILD_VERSION', 'dev'),
#     environment=os.getenv('BUILD_VERSION', 'dev'),
# )

config_app = ConfigHelper()

logger = ColoredLogger.get_logger(__name__, level=LEVEL_MAPPING.get(config_app.get_internal_log_level(), logging.INFO))

logger.info('VUI API starting...')
logger.info('loading config...')
infoService = InfoService()

config_app.create_env_variables()

if config_app.validate_env_variables():
    exit(200)

# server setting
k8s_in_cluster_mode = config_app.k8s_in_cluster_mode()
is_in_container_mode = config_app.container_mode()
endpoint_url = config_app.get_endpoint_url()
endpoint_port = config_app.get_endpoint_port()
limit_concurrency = config_app.get_limit_concurrency()
log_level = config_app.get_internal_log_level()
velero_cli_version = config_app.get_velero_version()
velero_cli_source = config_app.get_velero_version_folder()
velero_cli_destination = config_app.get_velero_dest_folder()

# LS 2024.02.22 add custom folder
velero_cli_source_custom = config_app.get_velero_version_custom_folder()

app_reload = config_app.uvicorn_reload_update()
logger.debug(f"App name: {__app_name__}, Version={__version__}")

logger.debug(f"run server at url:{endpoint_url}, port={endpoint_port}")
logger.debug(f"uvicorn log level:{log_level}, limit concurrency : {limit_concurrency}")
logger.debug(f"uvicorn reload: {app_reload}")
if k8s_in_cluster_mode:
    logger.debug(f"velero client version :{velero_cli_version}")
    logger.debug(f"velero client source .tar.gz :{velero_cli_source}")
    logger.debug(f"velero client destination :{velero_cli_destination}")

# use only for tests the env init on develop environment
skip_download = config_app.developer_mode_skip_download()

# Prepare environment
if (k8s_in_cluster_mode or is_in_container_mode) or not skip_download:
    output = asyncio.run(infoService.identify_architecture())
    if not output['success']:
        logger.error("Error in architecture identification.")
        exit(1)
    arch = output['data']['arch']
    VeleroClient(source_path=velero_cli_source,
                 source_path_user=velero_cli_source_custom,
                 destination_path=velero_cli_destination,
                 arch=arch,
                 version=velero_cli_version)

if __name__ == '__main__':
    # LS init database and default user (if not exits)
    # create database session
    db = SessionLocal()
    logger.debug("Open database connection for check default user")
    # Create default user
    create_default_user(db)

    # user config e secret managed in db
    # create_default_config(db)
    # create_default_secret_services(db)

    # Close
    db.close()
    logger.debug("Close database connection")


    def start_uvicorn():
        uvicorn.run('app:app',
                    host=endpoint_url,
                    port=int(endpoint_port),
                    reload=app_reload,
                    log_level=log_level,
                    workers=2,
                    limit_concurrency=int(limit_concurrency),
                    )


    server_process = Process(target=start_uvicorn)
    server_process.start()
    time.sleep(2)

    from helpers.nats_manager import boot_nats_start_manager

    if config_app.get_enable_nats():
        from app import app

        asyncio.run(boot_nats_start_manager(app))

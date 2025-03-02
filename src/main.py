import uvicorn
import asyncio
from multiprocessing import Process
import time

from app_data import __version__, __app_name__

from database.db_connection import SessionLocal
from security.authentication.built_in_authentication.users import create_default_user

from utils.logger_boot import logger

# kubernetes boot
from kubernetes_boot import config

# logger filter
from uvicorn_filter import uvicorn_logger
from configs.config_boot import config_app

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


logger.info('VUI API starting...')
logger.info('loading config...')

config_app.create_env_variables()

if config_app.validate_env_variables():
    exit(200)

logger.debug(f"App name: {__app_name__}, Version={__version__}")
logger.debug(f"run server at url:{config_app.api.endpoint_url}, port={config_app.api.endpoint_port}")
logger.debug(
    f"uvicorn log level:{config_app.logger.debug_level}, limit concurrency : "
    f"{config_app.security.limit_concurrency}")
logger.debug(f"uvicorn reload: {config_app.app.uvicorn_reload}")

if __name__ == '__main__':

    #
    # init database and default user (if not exits)
    #

    # create database session
    db = SessionLocal()
    logger.debug("Open database connection for check default user")
    # Create default user
    create_default_user(db)

    # Close
    db.close()
    logger.debug("Close database connection")


    def start_uvicorn():
        uvicorn.run('app:app',
                    host=config_app.api.endpoint_url,
                    port=config_app.api.endpoint_port,
                    reload=config_app.app.uvicorn_reload,
                    log_level=config_app.logger.debug_level,
                    workers=2,
                    limit_concurrency=config_app.security.limit_concurrency
                    )


    server_process = Process(target=start_uvicorn)
    server_process.start()
    time.sleep(2)

    from integrations.nats_manager import boot_nats_start_manager

    if config_app.nats.enable:
        from app import app

        asyncio.run(boot_nats_start_manager(app))

import uvicorn
import asyncio

from app_data import __version__, __app_name__

from security.helpers.database import SessionLocal
from security.service.helpers.users import create_default_user

from service.info_service import InfoService

from helpers.velero_client import VeleroClient
from helpers.printer import PrintHelper

from core.config import ConfigHelper

config_app = ConfigHelper()

print_ls = PrintHelper('[main]',
                       level=config_app.get_internal_log_level())
print_ls.info('start')
print_ls.info('load config')
infoService = InfoService()

# LS 2024.03.31 add
config_app.create_env_variables()

if config_app.validate_env_variables():
    exit(200)

# server setting
k8s_in_cluster_mode = config_app.k8s_in_cluster_mode()
is_in_container_mode = config_app.container_mode()
endpoint_url = config_app.get_endpoint_url()
endpoint_port = config_app.get_endpoint_port()
limit_concurrency = config_app.get_limit_concurrency()
log_level = config_app.logger_level()
velero_cli_version = config_app.get_velero_version()
velero_cli_source = config_app.get_velero_version_folder()
velero_cli_destination = config_app.get_velero_dest_folder()

# LS 2024.02.22 add custom folder
velero_cli_source_custom = config_app.get_velero_version_custom_folder()

app_reload = config_app.uvicorn_reload_update()
print_ls.info(f"start :{__app_name__} -version={__version__}")

print_ls.info(f"run server at url:{endpoint_url}-port={endpoint_port}")
print_ls.info(f"uvicorn log level:{log_level}-limit concurrency : {limit_concurrency}")
print_ls.info(f"uvicorn reload: {app_reload}")
if k8s_in_cluster_mode:
    print_ls.info(f"velero client version :{velero_cli_version}")
    print_ls.info(f"velero client source .tar.gz :{velero_cli_source}")
    print_ls.info(f"velero client destination :{velero_cli_destination}")

# use only for tests the env init on develop environment
skip_download = config_app.developer_mode_skip_download()

# Prepare environment
if (k8s_in_cluster_mode or is_in_container_mode) or not skip_download:
    output = asyncio.run(infoService.identify_architecture())
    if not output['success']:
        print_ls.error("Error in architecture identification.")
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
    print("INFO:     Open database connection")
    # Create default user
    create_default_user(db)
    # Close
    db.close()
    print("INFO:     Close database connection")

    uvicorn.run('app:app',
                host=endpoint_url,
                port=int(endpoint_port),
                reload=app_reload,
                log_level=log_level,
                workers=4,
                limit_concurrency=int(limit_concurrency),
                )

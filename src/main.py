import uvicorn
from utils.app_data import __version__, __app_name__

from libs.binary_velero_client import BinaryVeleroClient

from helpers.printer_helper import PrintHelper
from libs.config import ConfigEnv

print_ls = PrintHelper('main')
print_ls.info('start')

print_ls.info('load config')
config_app = ConfigEnv()

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

app_reload = config_app.uvicorn_reload_update()
print_ls.info(f"start :{__app_name__} -version={__version__}")

print_ls.info(f"run server at url:{endpoint_url}-port={endpoint_port}")
print_ls.info(f"uvicorn log level:{log_level}-limit concurrency : {limit_concurrency}")
if k8s_in_cluster_mode:
    print_ls.info(f"velero client version :{velero_cli_version}")
    print_ls.info(f"velero client source .tar.gz :{velero_cli_source}")
    print_ls.info(f"velero client destination :{velero_cli_destination}")

# Prepare environment
if k8s_in_cluster_mode or is_in_container_mode:
    clCLI_version = BinaryVeleroClient(velero_cli_source,
                                       velero_cli_destination,
                                       velero_cli_version)


if __name__ == '__main__':
    uvicorn.run('app:app',
                host=endpoint_url,
                port=int(endpoint_port),
                reload=app_reload,
                log_level=log_level,
                workers=1,
                limit_concurrency=int(limit_concurrency),
                )

from kubernetes import config

from configs.config_boot import config_app

from utils.logger_boot import logger



# Load Kubernetes configuration
try:
    config.load_incluster_config()
    logger.info("Kubernetes in cluster mode....")
except config.ConfigException:
    # Use local kubeconfig file if running locally
    config.load_kube_config(config_file=config_app.get_kube_config())
    logger.info("Kubernetes load local kube config...")


# from kubernetes import config, client
# from configs.config_boot import config_app
# from utils.logger import ColoredLogger, LEVEL_MAPPING
# import logging
# import http.client as http_client
#
# 
#
# logger = ColoredLogger.get_logger(__name__, level=LEVEL_MAPPING.get(config_app.get_internal_log_level(), logging.INFO))
#
# # Enable HTTP debugging
# http_client.HTTPConnection.debuglevel = 1  # Enables debug output for HTTP requests
#
# # Configure logging for API requests
# logging.basicConfig(level=logging.DEBUG)
# requests_log = logging.getLogger("urllib3")
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = True
#
# def log_request_response(func):
#     """Decorator to log Kubernetes API requests and responses."""
#     def wrapper(*args, **kwargs):
#         logger.info(f"📡 API Request: {func.__name__} - Args: {args} - Kwargs: {kwargs}")
#         try:
#             response = func(*args, **kwargs)
#             logger.info(f"✅ API Response: {func.__name__} - Response: {response}")
#             return response
#         except Exception as e:
#             logger.error(f"❌ API Error in {func.__name__}: {str(e)}")
#             raise
#     return wrapper
#
# # Load Kubernetes configuration
# try:
#     config.load_incluster_config()
#     logger.info("Kubernetes in cluster mode....")
# except config.ConfigException:
#     config.load_kube_config(config_file=config_app.get_kube_config())
#     logger.info("Kubernetes load local kube config...")
#
# # Patch Kubernetes API Client methods with the logging wrapper
# custom_api = client.CustomObjectsApi()
# custom_api.list_namespaced_custom_object = log_request_response(custom_api.list_namespaced_custom_object)
# custom_api.get_namespaced_custom_object = log_request_response(custom_api.get_namespaced_custom_object)
# custom_api.create_namespaced_custom_object = log_request_response(custom_api.create_namespaced_custom_object)
# custom_api.delete_namespaced_custom_object = log_request_response(custom_api.delete_namespaced_custom_object)

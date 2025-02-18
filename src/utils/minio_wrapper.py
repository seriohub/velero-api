import re

from minio import S3Error, Minio
from core.config import ConfigHelper
from service.backup_location_service import BackupLocationService

from helpers.logger import ColoredLogger, LEVEL_MAPPING
import logging

config_app = ConfigHelper()
logger = ColoredLogger.get_logger(__name__, level=LEVEL_MAPPING.get(config_app.get_internal_log_level(), logging.INFO))
bsl = BackupLocationService()


class MinioInterface:
    def __init__(self):
        logger.debug("init MinioInterface")

    def __extract_parts(self, url):
        logger.debug(f"extract_parts")
        # Define the regular expression pattern to extract the endpoint, bucket name, and backup name
        # pattern = r"s3:(http://[^/]+)/([^/]+)/(.+)"
        pattern = r"s3:(http[s]?://)?([^/]+)/([^/]+)/(.+)"
        # Search for the pattern in the given URL
        match = re.search(pattern, url)

        # If a match is found, return the captured groups (endpoint, bucket name, backup name)
        if match:
            protocol = match.group(1) or ''
            endpoint = match.group(2)
            bucket_name = match.group(3)
            backup_name = match.group(4)
            secure = protocol.strip('://') == 'https'
            logger.info(f"Protocol:{protocol}")
            logger.info(f"Endpoint:{endpoint}")
            logger.info(f"bucket_name:{bucket_name}")
            logger.info(f"backup_name:{backup_name}")
            return endpoint, bucket_name, backup_name, secure
        else:
            return None, None, None

    async def get_backup_size(self,
                              repository_url: str = None,
                              endpoint: str = None,
                              backup_storage_location: str = None,
                              bucket_name: str = None,
                              repository_name: str = None,
                              repository_type: str = None,
                              volume_namespace: str = None):

        logger.info("get_size")
        logger.info(f"get_size: repository_name={repository_url}")

        logger.info(f"get_size: endpoint={endpoint} "
                    f"-backup storage location={backup_storage_location} "
                    f"-repository name={repository_name} ")

        control_passed = False
        secure = None
        if endpoint is not None and volume_namespace is not None and backup_storage_location is not None:
            if len(endpoint) > 0 and len(volume_namespace) > 0 and len(backup_storage_location) > 0:
                logger.info(f"get_size:"
                            f"\n- endpoint={endpoint}"
                            f"\n- backup storage location={backup_storage_location}"
                            f"\n- volume name={volume_namespace} ")
                control_passed = True
        else:
            if repository_url is not None and len(repository_url) > 0:
                logger.debug(f"get_size: parse urls")

                endpoint, bucket_storage_location, volume_namespace, secure = self.__extract_parts(url=repository_url)
                if len(endpoint) > 0 and len(volume_namespace) > 0 and len(bucket_storage_location) > 0:
                    control_passed = True

        if control_passed:
            aws_access_key, aws_secret_key = await bsl.credentials(backup_storage_location)
            # aws_access_key = config.get_aws_key_id()
            # aws_secret_key = config.get_aws_access_key()
            if secure:
                aws_secure_connection = secure
            else:
                aws_secure_connection = config_app.get_aws_secure_connection()

            if len(aws_access_key) > 0 and len(aws_secret_key) > 0:
                minio_client = MinioClientWrapper(
                    endpoint=endpoint,
                    access_key=aws_access_key,
                    secret_key=aws_secret_key,
                    secure=aws_secure_connection  # Use SSL/TLS
                )
                files, total_size_mb = await minio_client.get_total_size_mb(bucket_name=bucket_name,
                                                                            prefix=repository_type + '/' +
                                                                                   volume_namespace)
                data = {'files': files, 'total_size_mb': total_size_mb}
                return {'success': True, 'data': data}
            else:
                return {'success': False, 'error': {
                    'title': 'Error',
                    'description': 'No AWS env parameters are found'
                }}
        else:
            return {'success': False, 'error': {
                'title': 'Error',
                'description': 'No parameters passed'
            }}


class MinioClientWrapper:
    def __init__(self, endpoint, access_key, secret_key, secure=True):
        self.client = Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=secure)

    async def list_files_with_sizes(self, bucket_name, prefix):
        try:
            logger.info(f"list_files_with_sizes: bucket_name:{bucket_name}- prefix:{prefix}")
            objects = self.client.list_objects(bucket_name, prefix=prefix, recursive=True)
            files_with_sizes = []
            files = 0
            files_total = 0
            for obj in objects:
                files_total += 1
                # logger.debug(f"{obj.object_name}- last modified: {obj.last_modified} size: {obj.size} ")
                if not obj.is_dir:
                    files += 1
                    files_with_sizes.append((obj.object_name, obj.size))
                else:
                    logger.debug(f"{obj.object_name}- Discard is dir ")
            # files_with_sizes = [(obj.object_name, obj.size) for obj in objects]
            logger.debug(f"Report: filtered:{files}/{files_total}")

            return files_with_sizes
        except S3Error as err:
            logger.error(f"An error occurred: {err}")
            return None

    async def get_total_size_mb(self, bucket_name, prefix):
        logger.info(f"get_total_size_mb: bucket_name:{bucket_name}- prefix:{prefix}")
        files_with_sizes = await self.list_files_with_sizes(bucket_name, prefix)
        if files_with_sizes is None:
            logger.warning(f"No files found")
            return None

        total_size_bytes = sum(size for _, size in files_with_sizes)
        total_size_mb = round(total_size_bytes / (1024 * 1024), 0)  # Convert bytes to MB
        logger.info(f"Bucket {bucket_name} size :{total_size_mb}Mb - files:{len(files_with_sizes)}")

        return len(files_with_sizes), total_size_mb

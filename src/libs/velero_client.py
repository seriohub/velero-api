import os
import sys
import tarfile
import traceback

import requests

from helpers.handle_exceptions import handle_exceptions_instance_method
from helpers.printer_helper import PrintHelper
from libs.config import ConfigEnv

config_app = ConfigEnv()

# class syntax
class VeleroClient:
    def __init__(self, source_path=None, destination_path=None, arch=None, version=None):
        self.print_ls = PrintHelper('[Velero client]')
        self.source_path = source_path
        self.destination_path = destination_path
        self.arch = arch
        self.version = version
        self.extension = 'tar.gz'
        self.init_velero_cli()

    def check_source_folder(self):
        # Check if the source folder exists
        if not os.path.exists(self.source_path):
            self.print_ls.error(f"Source folder '{self.source_path}' does not exist.")
            return False
        return True

    def check_destination_folder(self):
        # Check if the source folder exists
        if not os.path.exists(self.source_path):
            self.print_ls.error(f"Destination folder '{self.source_path}' does not exist.")
            return False
        return True

    def download_file(self, url, save_path):
        try:

            # Make the request to obtain the contents of the file
            response = requests.get(url)
            response.raise_for_status()  # Raises an exception if the request is unsuccessful

            self.print_ls.debug(f"Download url request successful")

            # Get file name from URL
            file_name = os.path.basename(url)

            # Merge file name with save path
            file_path = os.path.join(save_path, file_name)

            # Write the content in the file
            with open(file_path, 'wb') as file:
                file.write(response.content)

            self.print_ls.debug(f"Download url: {url}, save path:{file_path}")
            self.print_ls.info(f"Success download file: {file_path}")
            return file_path

        # LS 2024.02.19 handles different type of errors
        except requests.exceptions.ConnectionError as ce:
            # Handle connection errors (e.g., connection refused)
            self.print_ls.error(f"Download file error. Connection refused. "
                                f"Make sure the server is reachable and the URL is correct. error: {ce}")
            return None
        except (OSError, PermissionError) as ose:
            # Handle errors related to lack of internet access permissions
            self.print_ls.error(f"Download file error. "
                                f"Error: Lack of internet access permissions. "
                                f"Check your network settings. error {ose} ")
            return None
        except requests.exceptions.RequestException as re:
            # Handle other types of exceptions
            self.print_ls.error(f"Download file error. An error occurred: {re}")
            return None
        except Exception as e:
            self.print_ls.error(f"Download file error: {e}")
            return None

    # LS 2024.02.19 add to comment handle exceptions
    # @handle_exceptions_instance_method
    def __get_file(self, source_path):
        try:
            files = [file for file in os.listdir(source_path) if file.endswith(self.extension)]
            if not files:
                return None  # No files found with the given extension in the folder

            if self.version is not None:
                filename = f"velero-{self.version}-linux-{self.arch}.{self.extension}"
                if filename:
                    matching_files = [file for file in files if filename in file]
                    if matching_files:
                        matching_files.sort(key=lambda x: os.path.getmtime(os.path.join(source_path, x)))
                        return os.path.join(source_path, matching_files[0])

            # fallback client
            self.print_ls.wrn('Use fallback client velero...')
            files = list(filter(lambda k: self.arch in k, files))
            return os.path.join(source_path, files[-1])
        except:
            return None

    @handle_exceptions_instance_method
    def __extract_tarball__(self, source_tarball, destination_folder, file_to_extract='velero'):
        self.print_ls.info(f'extract_tarball {source_tarball}')

        # Check if the source tarball exists and it is a valid tar.gz file
        if not (os.path.exists(source_tarball) and tarfile.is_tarfile(source_tarball)):
            self.print_ls.error(f"{source_tarball} is not a valid tarball file.")
            return False

        # Check if the destination folder exists
        if not os.path.exists(destination_folder):
            self.print_ls.error(f"Destination folder '{destination_folder}' does not exist.")
            return False

        try:
            with tarfile.open(source_tarball, 'r:gz') as tar:
                # tar.extractall(destination_folder)
                members = tar.getmembers()

                # If file_to_extract is specified, extract only that file
                if file_to_extract:
                    for member in members:
                        # print("member.name", member.name)
                        if member.name.endswith(file_to_extract):
                            # print(member)
                            # Get the base folder name (assuming the tarball has only one top-level folder)
                            # base_folder = os.path.dirname(member.name)
                            # tar.extract(member, os.path.join(destination_folder, base_folder))
                            member.name = os.path.basename(member.name)
                            tar.extract(member.name, destination_folder)
                            self.print_ls.info(
                                f"Successfully extracted '{file_to_extract}' from '{source_tarball}' to '{destination_folder}'.")
                            return True
                else:
                    tar.extractall(destination_folder)
                    self.print_ls.info(
                        f"Successfully extracted all files from '{source_tarball}' to '{destination_folder}'.")
                    return True
            self.print_ls.info(f"Successfully extracted '{source_tarball}' to '{destination_folder}'.")
            return True

        except tarfile.TarError as e:
            self.print_ls.error(f"Error occurred while extracting '{source_tarball}': {e}")
            return False

    # LS 2024.02.19 add to comment handle exceptions
    # @handle_exceptions_instance_method
    def init_velero_cli(self):
        try:
            self.print_ls.info(f'architecture: {self.arch}, client-version:{self.version}')
            self.print_ls.info(f'source folder: {self.source_path}')
            self.print_ls.info(f'destination folder: {self.destination_path}')

            if self.version != '' and self.arch != '':
                if not config_app.developer_mode_skip_download():
                    url = f"https://github.com/vmware-tanzu/velero/releases/download/{self.version}/velero-{self.version}-linux-{self.arch}.tar.gz"
                    self.download_file(save_path=self.source_path + '/dl', url=url)
                else:
                    self.print_ls.info(f'developer mode- download skipped')

            if not self.check_source_folder():
                raise RuntimeError('Source folder not exist')

            if not self.check_destination_folder():
                raise RuntimeError('Destination folder not exist')

            file_to_extract = self.__get_file(source_path=self.source_path + '/dl')
            if file_to_extract is None:
                file_to_extract = self.__get_file(source_path=self.source_path)

            self.print_ls.info(f'velero client compress file: {file_to_extract}')

            if file_to_extract is None:
                self.print_ls.error(f"No valid (None) tarball file.")
                raise RuntimeError(f"No valid (None) tarball file.")
            else:
                self.print_ls.info(f'file :{file_to_extract}')

                ret = self.__extract_tarball__(file_to_extract, self.destination_path)
                self.print_ls.info(f'Result from init velero-cli-version :{ret}')
                if not ret:
                    raise RuntimeError("Error extract velero")
        # LS 2024.02.19 more detailed error exception
        except Exception as Ex:
            self.print_ls.error(f"Init velero client failed.")
            _, _, tb = sys.exc_info()
            exc_type, exc_obj, exc_tb = sys.exc_info()
            message = ('E=%s, F=%s, L=%s' %
                       (str(Ex), traceback.extract_tb(exc_tb)[-1][0], traceback.extract_tb(exc_tb)[-1][1]))

            self.print_ls.error(f"{message}")
            self.print_ls.error(f"an forced exit code(100) is called")
            exit(100)

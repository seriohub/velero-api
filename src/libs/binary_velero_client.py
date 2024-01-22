import os
import tarfile

from helpers.handle_exceptions import handle_exceptions_instance_method
from helpers.printer_helper import PrintHelper


# class syntax
class BinaryVeleroClient:
    def __init__(self, binary_path, destination_path, version=None):
        self.print_ls = PrintHelper('velero_client')
        self.binary_path = binary_path
        self.destination_path = destination_path
        self.__init_velero_cli__(version)

    @handle_exceptions_instance_method
    def __get_file_version__(self, folder_path, extension='.tar.gz', filename=None):
        # Check if the destination folder exists
        if not os.path.exists(folder_path):
            self.print_ls.error(f"Source folder '{folder_path}' does not exist.")
            return None

        self.print_ls.info(f'__get_file_version__')
        files = [file for file in os.listdir(folder_path) if file.endswith(extension)]
        if not files:
            return None  # No files found with the given extension in the folder

        if filename:
            matching_files = [file for file in files if filename in file]
            if matching_files:
                matching_files.sort(key=lambda x: os.path.getmtime(os.path.join(folder_path, x)))
                return os.path.join(folder_path, matching_files[0])

        # fallback client
        files.sort(key=lambda x: x.lower())
        return os.path.join(folder_path, files[-1])

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
                            base_folder = os.path.dirname(member.name)
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

    @handle_exceptions_instance_method
    def __init_velero_cli__(self, version):
        self.print_ls.info(f'client-version :{version}')
        file_to_extract = self.__get_file_version__(folder_path=self.binary_path, filename=version)
        if file_to_extract is None:
            self.print_ls.error(f"No valid (None) tarball file.")
            return False
        else:
            self.print_ls.info(f'file :{file_to_extract}')

        if self.destination_path is None:
            self.print_ls.error(f"No valid (None) destination folder")
            return False

        ret = self.__extract_tarball__(file_to_extract, self.destination_path)
        self.print_ls.info(f'result from init velero-cli-version :{ret}')

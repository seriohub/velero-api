import json
import os

from fastapi import HTTPException

from utils.logger_boot import logger


async def get_folders_list(directory: str):
    """
    Returns a list of folders present in a given directory.

    :param directory: Directory path to be parsed
    :return: List of folders in the directory
    """
    try:
        # Get the list of directories in the given path
        return [{'name': f} for f in os.listdir(directory) if os.path.isdir(os.path.join(directory, f))]
    except FileNotFoundError:
        # Handle the case where the directory does not exist
        logger.error(f"Error: The directory '{directory}' does not exist.")
        # raise HTTPException(status_code=404, detail=f"Error: The directory '{directory}' does not exist.")
        return []
    except PermissionError:
        # Handle the case where access to the directory is denied
        logger.error(f"Error: Permission denied to access '{directory}'.")
        return []


async def get_directory_contents(directory: str):
    """
    Returns a dictionary containing lists of folders and files in a given directory.

    :param directory: Path of the directory to analyze
    :return: Dictionary with 'folders' and 'files' as keys
    """
    try:
        # Get the list of directories in the given path
        folders = [f for f in os.listdir(directory) if os.path.isdir(os.path.join(directory, f))]

        # Get the list of files in the given path
        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

        return {"folders": folders, "files": files}
    except FileNotFoundError:
        # Handle the case where the directory does not exist
        logger.error(f"Error: The directory '{directory}' does not exist.")
        return {"folders": [], "files": []}
    except PermissionError:
        # Handle the case where access to the directory is denied
        logger.error(f"Error: Permission denied to access '{directory}'.")
        return {"folders": [], "files": []}


async def read_json_file(file_path: str):
    """
    Reads the contents of a JSON file and returns the parsed data.

    :param file_path: Path to the JSON file
    :return: Parsed JSON data or None if an error occurs
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' does not exist.")
    except json.JSONDecodeError:
        print(f"Error: The file '{file_path}' is not a valid JSON file.")
    except Exception as e:
        print(f"Error: An unexpected error occurred - {e}")
    return None


async def get_recursive_directory_contents(directory: str):
    """
    Recursively retrieves the contents of a directory and formats them in the specified structure.

    :param directory: Path of the directory to analyze
    :return: List of dictionaries formatted as required
    """

    def build_tree(root_path):
        tree = []
        try:
            for item in os.listdir(root_path):
                item_path = os.path.join(root_path, item)
                relative_path = os.path.relpath(item_path, directory).replace("\\", "/")

                if os.path.isdir(item_path):
                    tree.append({"value": relative_path, "label": item, "children": build_tree(item_path)})
                else:
                    tree.append({"value": relative_path, "label": item})
        except PermissionError:
            print(f"Error: Permission denied to access '{root_path}'.")
        return tree

    return build_tree(directory)

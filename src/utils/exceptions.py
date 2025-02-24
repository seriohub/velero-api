import sys
from functools import wraps
import traceback

import os
from fastapi import HTTPException


# import sentry_sdk


def _get_relative_path(filepath):
    """Returns the relative path from the project root"""
    project_root = os.getcwd()  # Gets the current directory (where the main is running)
    return os.path.relpath(filepath, project_root)


def handle_exceptions_endpoint(fn):
    @wraps(fn)
    async def wrapper(*args, **kw):
        try:
            return await fn(*args, **kw)
        except Exception as Ex:
            _, _, exc_tb = sys.exc_info()
            tb_last = traceback.extract_tb(exc_tb)[-1]
            file_path = _get_relative_path(tb_last[0])  # Relative path
            line_number = tb_last[1]

            error_message = (f"Error: {Ex} | "
                             f"File: {file_path} | "
                             f"Function: {fn.__name__} | "
                             f"Line: {line_number}")

            print(error_message)

            output = {
                'title': 'An error occurred',
                'description': error_message
            }

            raise HTTPException(status_code=400, detail=output)
        finally:
            if 'exc_tb' in locals():
                del exc_tb

    return wrapper

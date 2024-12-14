import sys
from functools import wraps
import traceback
from fastapi.responses import JSONResponse
import os
#import sentry_sdk

# def handle_exceptions_instance_method(fn):
#     from functools import wraps
#
#     @wraps(fn)
#     def wrapper(self, *args, **kw):
#         try:
#             return fn(self, *args, **kw)
#         except Exception as Ex:
#             _, _, tb = sys.exc_info()
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             print('E=%s, F=%s, L=%s' % (
#                 str(Ex), traceback.extract_tb(exc_tb)[-1][0], traceback.extract_tb(exc_tb)[-1][1]))
#
#             return {'success': False, 'error': {'title': 'handle_exceptions_instance_method',
#                                                 'description': str(Ex) + str(traceback.extract_tb(exc_tb)[-1][0]) +
#                                                 ' - fn name: ' + str(fn.__name__) +
#                                                 ' - line: ' + str(traceback.extract_tb(exc_tb)[-1][1])
#                                                 }
#                     }
#         finally:
#             if 'tb' in locals():
#                 del tb
#
#     return wrapper


# def handle_exceptions_static_method(fn):
#     from functools import wraps
#
#     @wraps(fn)
#     def wrapper(*args, **kw):
#         try:
#             return fn(*args, **kw)
#         except Exception as Ex:
#             _, _, tb = sys.exc_info()
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             print('E=%s, F=%s, L=%s' % (
#                 str(Ex), traceback.extract_tb(exc_tb)[-1][0], traceback.extract_tb(exc_tb)[-1][1]))
#
#             return {'error': {'title': 'handle_exceptions_static_method',
#                               'description': str(Ex) + str(traceback.extract_tb(exc_tb)[-1][0]) +
#                                              ' - fn name: ' + str(fn.__name__) +
#                                              ' - line: ' + str(traceback.extract_tb(exc_tb)[-1][1])
#                               }
#                     }
#         finally:
#             if 'tb' in locals():
#                 del tb
#
#     return wrapper


# ok per service
def handle_exceptions_async_method(fn):
    @wraps(fn)
    async def wrapper(*args, **kw):
        try:
            return await fn(*args, **kw)
        except Exception as Ex:
            _, _, tb = sys.exc_info()
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print('E=%s, F=%s, L=%s' % (
                str(Ex), traceback.extract_tb(exc_tb)[-1][0], traceback.extract_tb(exc_tb)[-1][1]))

            #sentry_sdk.capture_exception(Ex)

            return {'success': False, 'error': {'title': 'Service method',
                                                'description': str(Ex) +
                                                               ' - file name: ' + os.path.basename(str(traceback.extract_tb(exc_tb)[-1][0])) +
                                                               ' - fn name: ' + str(fn.__name__) +
                                                               ' - line: ' + str(traceback.extract_tb(exc_tb)[-1][1])
                                                }
                    }
        finally:
            if 'tb' in locals():
                del tb

    return wrapper

def handle_exceptions_controller(fn):
    @wraps(fn)
    async def wrapper(*args, **kw):
        try:
            return await fn(*args, **kw)
        except Exception as Ex:
            _, _, tb = sys.exc_info()
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print('E=%s, F=%s, L=%s' % (
                str(Ex), traceback.extract_tb(exc_tb)[-1][0], traceback.extract_tb(exc_tb)[-1][1]))

            #sentry_sdk.capture_exception(Ex)

            output = {'error': {'title': 'Controller Error',
                                'description': str(Ex) +
                                               ' - file name: ' + os.path.basename(str(traceback.extract_tb(exc_tb)[-1][0])) +
                                               ' - fn name: ' + str(fn.__name__) +
                                               ' - line: ' + str(traceback.extract_tb(exc_tb)[-1][1])
                                }
                      }
            return JSONResponse(content=output, status_code=400)
        finally:
            if 'tb' in locals():
                del tb

    return wrapper

def handle_exceptions_endpoint(fn):
    @wraps(fn)
    async def wrapper(*args, **kw):
        try:
            return await fn(*args, **kw)
        except Exception as Ex:
            _, _, tb = sys.exc_info()
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print('E=%s, F=%s, L=%s' % (
                str(Ex), traceback.extract_tb(exc_tb)[-1][0], traceback.extract_tb(exc_tb)[-1][1]))

            #sentry_sdk.capture_exception(Ex)

            output = {'error': {'title': 'Endpoint Error',
                                'description': str(Ex) +
                                               ' - file name: ' + os.path.basename(str(traceback.extract_tb(exc_tb)[-1][0])) +
                                               ' - fn name: ' + str(fn.__name__) +
                                               ' - line: ' + str(traceback.extract_tb(exc_tb)[-1][1])
                                }
                      }
            return JSONResponse(content=output, status_code=400)
        finally:
            if 'tb' in locals():
                del tb

    return wrapper

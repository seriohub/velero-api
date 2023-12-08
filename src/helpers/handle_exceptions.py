import sys
from functools import wraps
import traceback


def handle_exceptions_instance_method(fn):
    from functools import wraps

    @wraps(fn)
    def wrapper(self, *args, **kw):
        try:
            return fn(self, *args, **kw)
        except Exception as Ex:
            _, _, tb = sys.exc_info()
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print("E=%s, F=%s, L=%s" % (
                str(Ex), traceback.extract_tb(exc_tb)[-1][0], traceback.extract_tb(exc_tb)[-1][1]))

            return {'error': {"description": str(Ex),
                              "file": traceback.extract_tb(exc_tb)[-1][0],
                              "fn name": fn.__name__,
                              "line": traceback.extract_tb(exc_tb)[-1][1]
                              }
                    }
        finally:
            if 'tb' in locals():
                del tb

    return wrapper


def handle_exceptions_static_method(fn):
    from functools import wraps

    @wraps(fn)
    def wrapper(*args, **kw):
        try:
            return fn(*args, **kw)
        except Exception as Ex:
            _, _, tb = sys.exc_info()
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print("E=%s, F=%s, L=%s" % (
                str(Ex), traceback.extract_tb(exc_tb)[-1][0], traceback.extract_tb(exc_tb)[-1][1]))

            return {'error': {"description": str(Ex),
                              "file": traceback.extract_tb(exc_tb)[-1][0],
                              "fn name": fn.__name__,
                              "line": traceback.extract_tb(exc_tb)[-1][1]
                              }
                    }
        finally:
            if 'tb' in locals():
                del tb

    return wrapper


def handle_exceptions_async_method(fn):
    @wraps(fn)
    async def wrapper(*args, **kw):
        try:
            return await fn(*args, **kw)
        except Exception as Ex:
            _, _, tb = sys.exc_info()
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print("E=%s, F=%s, L=%s" % (
                str(Ex), traceback.extract_tb(exc_tb)[-1][0], traceback.extract_tb(exc_tb)[-1][1]))

            return {'error': {"description": str(Ex),
                              "file": traceback.extract_tb(exc_tb)[-1][0],
                              "fn name": fn.__name__,
                              "line": traceback.extract_tb(exc_tb)[-1][1]
                              }
                    }
        finally:
            if 'tb' in locals():
                del tb

    return wrapper

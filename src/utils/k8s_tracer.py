from functools import wraps

from core.config import ConfigHelper
from helpers.connection_manager import manager
from helpers.printer import PrintHelper

config = ConfigHelper()
print_ls = PrintHelper('[k8s tracer]',
                       level=config.get_internal_log_level())


def trace_k8s_async_method(description):
    def decorator(fn):
        @wraps(fn)
        async def wrapper(*args, **kw):
            message = f"k8s {description}"
            # print("[k8s]", message)
            print_ls.debug(message)
            await manager.broadcast(message)
            return await fn(*args, **kw)

        return wrapper

    return decorator

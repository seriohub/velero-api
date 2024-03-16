from functools import wraps

from core.config import ConfigHelper
from core.context import current_user_var
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
            # await manager.broadcast(message)
            try:
                user = current_user_var.get()
                await manager.send_personal_message(str(user.id), message)
            except:
                pass
            return await fn(*args, **kw)

        return wrapper

    return decorator

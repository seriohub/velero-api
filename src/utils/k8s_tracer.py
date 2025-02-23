from functools import wraps
import json

from configs.config_boot import config_app
from configs.context import current_user_var
from ws.websocket_manager import manager

from utils.logger_boot import logger


def trace_k8s_async_method(description):
    def decorator(fn):
        @wraps(fn)
        async def wrapper(*args, **kw):
            message = f"k8s {description}"
            # await manager.broadcast(message)
            try:
                user = current_user_var.get()
                logger.debug(f"user:{user}, message:{message}")
                response = {'type': 'k8s_tracker', 'message': message}
                await manager.send_personal_message(str(user.id), json.dumps(response))
            except Exception as Ex:
                logger.warning(f"{str(Ex)}, message:{message}")
                pass
            return await fn(*args, **kw)

        return wrapper

    return decorator

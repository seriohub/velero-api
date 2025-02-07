from functools import wraps
import json

from core.config import ConfigHelper
from core.context import current_user_var
from helpers.connection_manager import manager

from helpers.logger import ColoredLogger, LEVEL_MAPPING
import logging

config_app = ConfigHelper()
logger = ColoredLogger.get_logger(__name__, level=LEVEL_MAPPING.get(config_app.get_internal_log_level(), logging.INFO))

def trace_k8s_async_method(description):
    def decorator(fn):
        @wraps(fn)
        async def wrapper(*args, **kw):
            message = f"k8s {description}"
            # await manager.broadcast(message)
            try:
                user = current_user_var.get()
                logger.debug(f"user:{user}, message:{message}")
                response = {'response_type': 'k8s_tracker', 'message': message}
                await manager.send_personal_message(str(user.id), json.dumps(response))
            except Exception as Ex:
                logger.warning(f"{str(Ex)}, message:{message}")
                pass
            return await fn(*args, **kw)

        return wrapper

    return decorator

from fastapi import Depends
from starlette.requests import Request

from contexts.context import current_user_var, cp_user, called_endpoint_var
from models.db.user import User
from security.authentication.built_in_authentication.users import logger
from security.authentication.tokens import get_user_entity_from_token


async def get_current_active_user(request: Request, current_user: User = Depends(get_user_entity_from_token)):
    # if current_user.is_disabled:
    #    raise HTTPException(status_code=400, detail='Inactive user')
    cu = current_user_var.set(current_user)

    if current_user.is_nats:
        cp_user.set(request.headers.get('cp_user'))
    # return current_user
    try:
        yield current_user
    finally:
        if called_endpoint_var.get().find('/stats/in-progress') == -1:
            logger.debug(
                f"Reset context current user {str(current_user_var.get().username)} endpoint: "
                f"{called_endpoint_var.get()}")
        current_user_var.reset(cu)

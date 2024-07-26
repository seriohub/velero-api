from contextvars import ContextVar

current_user_var = ContextVar('current_user')
called_endpoint_var = ContextVar("called_endpoint")
cp_user = ContextVar('control_plane_user')

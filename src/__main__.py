from vui_common.main import run_api
from vui_common.ws import ws_manager_proxy
from vui_common import app_data

from ws.ws_manager import WebSocketManager

app_data.__app_name__ = "VUI-API"
app_data.__app_summary__ = "VUI-API is part of VUI-Project"

ws_manager_proxy.ws_manager = WebSocketManager()

if __name__ == "__main__":
    run_api(app_module="main:app")

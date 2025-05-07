import asyncio
from ws.ws_manager import WebSocketManager
# from ws import ws_manager_proxy
from vui_common.ws import ws_manager_proxy

from integrations.nats_manager import NatsManager
from integrations import nats_manager_proxy

from k8s.k8s_watch_manager import K8sWatchManager
from k8s import k8s_watcher_proxy
from vui_common.configs.config_proxy import config_app

def init_watchers(app):
    ws_manager_proxy.ws_manager = WebSocketManager()
    if config_app.nats.enable:
        nats_manager_proxy.nat_manager = NatsManager(app)

    async def send_global_to_all(message: str):
        await ws_manager_proxy.ws_manager.broadcast(message)
        if config_app.nats.enable:
            await nats_manager_proxy.nat_manager.publish_global_event(message)

    async def send_user_to_all(user_id: str, message: str):
        await ws_manager_proxy.ws_manager.send_personal_message(user_id, message)
        if config_app.nats.enable:
            await nats_manager_proxy.nat_manager.publish_user_event(user_id, message)

    k8s_watcher_proxy.k8s_watcher_manager = K8sWatchManager(
        send_global_callback=send_global_to_all,
        send_user_callback=send_user_to_all
    )

    if config_app.nats.enable:
        asyncio.create_task(nats_manager_proxy.nat_manager.run())
    asyncio.create_task(k8s_watcher_proxy.k8s_watcher_manager.start_global_watch_tasks())

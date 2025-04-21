# import asyncio
# from fastapi import WebSocket, WebSocketDisconnect
# from typing import Dict
# import json
# import traceback
# # from kubernetes_asyncio import client, config, watch
from vui_common.configs.config_proxy import config_app
# # from security.authentication.tokens import get_user_from_token
# from security.authentication.tokens import get_user_entity_from_token
# from utils.logger_boot import logger
from k8s import k8s_watcher_proxy
#
# # socket manager
# class WebSocketManager:
#     def __init__(self):
#         # self.active_connections: List[WebSocket] = []
#         self.active_connections: Dict[str, WebSocket] = {}
#
#         self.watch_running = False  # Stato del watch globale
#         self.user_watch_tasks = {}  # Task personalizzati per utenti
#         self.watch_tasks = []  # Task globali
#
#     async def connect(self, websocket: WebSocket):
#         """Manages the WebSocket connection and authenticates the user only after receiving a valid token."""
#         try:
#             await websocket.accept()
#             user = None  # Initialize the user as None
#             auth_timeout = 5  # Tempo massimo in secondi per autenticarsi
#
#             while user is None:  # Continue until it receives a valid token
#                 try:
#                     message = await asyncio.wait_for(websocket.receive_text(), timeout=auth_timeout)
#                     data = json.loads(message) if message.startswith('{') else message
#                 except asyncio.TimeoutError:
#                     logger.info("Timeout without authentication. Keeping connection open for pings only.")
#                     break  # Esce dal loop di autenticazione e permette solo ping
#                 except WebSocketDisconnect as e:
#                     if e.code == 1005:
#                         logger.warning("Client disconnected without a status code (1005)")
#                     else:
#                         logger.info(f"WebSocket disconnected with code {e.code}: {e.reason}")
#                     return
#                 except Exception as e:
#                     logger.error(f"WebSocket Receive Error: {e}")
#                     traceback.print_exc()
#                     return  # Terminate the connection if there is an error in receiving the message
#
#                 if isinstance(data, dict) and "action" in data and data["action"] == "ping":
#                     # Responds to ping to keep the connection open
#                     await websocket.send_text(json.dumps({"action": "pong"}))
#                     continue  # Continue to receive messages without closing the connection
#
#                 elif isinstance(data, str):
#                     # Treats the message as a JWT token
#                     user = await get_user_entity_from_token(data)
#
#                     #
#                     # uncomment to enable session with cookies (no 3/3)
#                     #
#                     # user = await get_user_entity_from_token(token=websocket.cookies.get("auth_token"))
#
#                 if user:
#                     self.active_connections[str(user.id)] = websocket
#                     response = {'response_type': 'notification', 'message': 'Connection READY!'}
#                     await self.send_personal_message(str(user.id), json.dumps(response))
#
#                     # If global watch is not active, start it
#                     # await self.start_global_watch_tasks() ############# aaa
#                     # await self.watch_user_resource(str(user.id), "backups")
#
#                     # Start listening to messages for authenticated users only
#                     await self.listen_for_messages(websocket, str(user.id))
#                     return  # Ends the loop after authenticating the user
#
#             # If no valid token has been received
#             try:
#                 while True:
#                     message = await asyncio.wait_for(websocket.receive_text(),
#                                                      timeout=30)  # only pings allowed
#                     data = json.loads(message) if message.startswith('{') else message
#                     if isinstance(data, dict) and "action" in data and data["action"] == "ping":
#                         await websocket.send_text(json.dumps({"action": "pong"}))
#                     else:
#                         logger.warning("Unauthenticated client tried to send a message. Closing connection.")
#                         await websocket.close(1001)
#                         return
#             except asyncio.TimeoutError:
#                 logger.info("Closing unauthenticated connection after inactivity.")
#                 await websocket.close(1001)
#             except WebSocketDisconnect:
#                 logger.info("Unauthenticated WebSocket disconnected.")
#             except Exception as e:
#                 logger.error(f"Error in unauthenticated WebSocket handling: {e}")
#                 await websocket.close(1001)
#
#         except WebSocketDisconnect:
#             logger.debug("WebSocket disconnected")
#             await websocket.close(1001)
#         except Exception as e:
#             logger.error(f"WebSocket connection error: {e}")
#             await websocket.close(1001)
#
#     async def disconnect_websocket(self, websocket: WebSocket):
#         user_id = None
#         for uid, conn in self.active_connections.items():
#             if conn == websocket:
#                 user_id = uid
#                 break
#         if user_id:
#             try:
#                 await websocket.close(code=1001)
#             except Exception:
#                 logger.warning(f"WebSocket for user {user_id} was already closed.")
#             finally:
#                 self.active_connections.pop(user_id, None)
#                 logger.debug(f"Disconnected user {user_id} and removed from active connections.")
#
#     def disconnect(self, user_id):
#         self.active_connections[user_id].close(1001)
#         del self.active_connections[user_id]
#
#     async def send_personal_message(self, user_id, message: str):
#         try:
#             await self.active_connections[str(user_id)].send_text(message)
#         except KeyError:
#             logger.warning(f"User ID {user_id} not found in active connections.")
#         except AttributeError:
#             logger.error(f"Connection object for user ID {user_id} does not support send_text method.")
#         except Exception as e:
#             logger.error(f"An unexpected error occurred while sending message to user ID {user_id}: {str(e)}")
#
#     async def broadcast(self, message: str):
#         for user_id in self.active_connections:
#             try:
#                 await self.active_connections[user_id].send_text(message)
#             except Exception as Ex:
#                 logger.error("error", Ex)
#
#     async def listen_for_messages(self, websocket: WebSocket, user_id: str):
#         """Listen for incoming messages from the client"""
#         logger.info(f"Start listen for incoming messages from the client.....")
#         try:
#             while True:
#                 message = await websocket.receive_text()
#                 if message != '{"action":"ping"}':
#                     logger.info(f"Received message from user {user_id}: {message}")
#
#                 # Handle different types of messages
#                 try:
#                     data = json.loads(message)
#                     if "action" in data:
#                         if data["action"] == "ping":
#                             await websocket.send_text(json.dumps({"action": "pong"}))
#                         if data["action"] == "watch" and "plural" in data.keys() and isinstance(data.get("plural"), str):
#                             try:
#                                 # await self.watch_user_resource(user_id=user_id, plural=data["plural"], namespace=config_app.k8s.velero_namespace)
#                                 if k8s_watcher_proxy.k8s_watcher_manager is not None:
#                                     await k8s_watcher_proxy.k8s_watcher_manager.watch_user_resource(user_id=user_id, plural=data["plural"], namespace=config_app.k8s.velero_namespace)
#                             except Exception as e:
#                                 logger.error(f"Error in watch_user_resource: {e}, user_id={user_id}, plural={data['plural']}, namespace={config_app.k8s.velero_namespace}")
#                                 if hasattr(self, 'watch_user_resource'):
#                                     logger.watch("watch_user_resource exists")
#                                 else:
#                                     logger.watch("watch_user_resource not exists")
#
#                         if data["action"] == "watch:clear":
#                             try:
#                                 # await self.clear_watch_user_resource(user_id)
#                                 if k8s_watcher_proxy.k8s_watcher_manager is not None:
#                                     await k8s_watcher_proxy.k8s_watcher_manager.clear_watch_user_resource(user_id)
#                             except Exception as e:
#                                 logger.error(f"Error in clear_watch_user_resource: {e}")
#
#                         # elif data["action"] == "broadcast":
#                         #     await self.broadcast(json.dumps({"message": data.get("message", "")}))
#                         # elif data["action"] == "private_message":
#                         #     target_user = data.get("target_user")
#                         #     msg = data.get("message", "")
#                         #     if target_user:
#                         #         await self.send_personal_message(target_user, msg)
#
#                     else:
#                         logger.error("Invalid message format.")
#                 except json.JSONDecodeError:
#                     logger.error(f"Invalid JSON message from user {user_id}: {message}")
#
#         except WebSocketDisconnect:
#             logger.warning(f"User {user_id} disconnected.")
#             await self.disconnect_websocket(websocket)
#
#         except Exception as e:
#             logger.error(f"Error in listen_for_messages: {e}")
#             await self.disconnect_websocket(websocket)



import json

from vui_common.ws.base_manager import WebSocket
from vui_common.logger.logger_proxy import logger
from vui_common.ws.base_manager import BaseWebSocketManager
from vui_common.ws.ws_message import WebSocketMessage, build_message

from integrations import nats_manager_proxy

class WebSocketManager(BaseWebSocketManager):
    def __init__(self):
        super().__init__()

    # 🔁 Hook: override
    async def on_user_authenticated(self, user_id: str):
        logger.debug(f"on_user_authenticated override method {user_id}")

    # 🔁 Hook: override
    async def handle_custom_action(self, user_id: str, data: WebSocketMessage, websocket: WebSocket):
        try:
            logger.info(f"Received message from user {user_id}: request: {data} {data.kind} {data.type}")

            if data.kind == 'command' and data.type == "watch":
                if k8s_watcher_proxy.k8s_watcher_manager is not None:
                    # await k8s_watcher_proxy.k8s_watcher_manager.watch_user_resource(data.payload.get('agent_name'), data.payload.get('plural'),namespace=config_app.k8s.velero_namespace)
                    await k8s_watcher_proxy.k8s_watcher_manager.watch_user_resource(user_id=user_id,
                                                                                    plural=data.payload.get("plural"),
                                                                                    namespace=config_app.k8s.velero_namespace)
                else:
                    print("is none")

            elif data.kind == 'command' and data.type == "watch_clear":
                if k8s_watcher_proxy.k8s_watcher_manager is not None:
                    await k8s_watcher_proxy.k8s_watcher_manager.clear_watch_user_resource(user_id)
                else:
                    print("is none")

            else:
                logger.warning(f"Unhandled action from {user_id}: {data}")
        except Exception as e:
            logger.error(f"Error handle_custom_action: {e} - {data}")

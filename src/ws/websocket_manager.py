import asyncio
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict
import json
import traceback
from kubernetes_asyncio import client, config, watch
from configs.config_boot import config_app
# from security.authentication.tokens import get_user_from_token
from security.authentication.tokens import get_user_entity_from_token
from utils.logger_boot import logger


# socket manager
class WebSocketManager:
    def __init__(self):
        # self.active_connections: List[WebSocket] = []
        self.active_connections: Dict[str, WebSocket] = {}

        self.watch_running = False  # Stato del watch globale
        self.user_watch_tasks = {}  # Task personalizzati per utenti
        self.watch_tasks = []  # Task globali

    async def connect(self, websocket: WebSocket):
        """Manages the WebSocket connection and authenticates the user only after receiving a valid token."""
        try:
            await websocket.accept()
            user = None  # Initialize the user as None
            auth_timeout = 5  # Tempo massimo in secondi per autenticarsi

            while user is None:  # Continue until it receives a valid token
                try:
                    message = await asyncio.wait_for(websocket.receive_text(), timeout=auth_timeout)
                    data = json.loads(message) if message.startswith('{') else message
                except asyncio.TimeoutError:
                    logger.info("Timeout without authentication. Keeping connection open for pings only.")
                    break  # Esce dal loop di autenticazione e permette solo ping
                except WebSocketDisconnect as e:
                    if e.code == 1005:
                        logger.warning("Client disconnected without a status code (1005)")
                    else:
                        logger.info(f"WebSocket disconnected with code {e.code}: {e.reason}")
                    return
                except Exception as e:
                    logger.error(f"WebSocket Receive Error: {e}")
                    traceback.print_exc()
                    return  # Terminate the connection if there is an error in receiving the message

                if isinstance(data, dict) and "action" in data and data["action"] == "ping":
                    # Responds to ping to keep the connection open
                    await websocket.send_text(json.dumps({"type": "pong"}))
                    continue  # Continue to receive messages without closing the connection

                elif isinstance(data, str):
                    # Treats the message as a JWT token
                    user = await get_user_entity_from_token(data)

                    #
                    # uncomment to enable session with cookies (no 3/3)
                    #
                    # user = await get_user_entity_from_token(token=websocket.cookies.get("auth_token"))

                if user:
                    self.active_connections[str(user.id)] = websocket
                    response = {'response_type': 'notification', 'message': 'Connection READY!'}
                    await self.send_personal_message(str(user.id), json.dumps(response))

                    # If global watch is not active, start it
                    await self.start_global_watch_tasks()
                    # await self.watch_user_resource(str(user.id), "backups")

                    # Start listening to messages for authenticated users only
                    await self.listen_for_messages(websocket, str(user.id))
                    return  # Ends the loop after authenticating the user

            # If no valid token has been received
            try:
                while True:
                    message = await asyncio.wait_for(websocket.receive_text(),
                                                     timeout=30)  # only pings allowed
                    data = json.loads(message) if message.startswith('{') else message
                    if isinstance(data, dict) and "action" in data and data["action"] == "ping":
                        await websocket.send_text(json.dumps({"type": "pong"}))
                    else:
                        logger.warning("Unauthenticated client tried to send a message. Closing connection.")
                        await websocket.close(1001)
                        return
            except asyncio.TimeoutError:
                logger.info("Closing unauthenticated connection after inactivity.")
                await websocket.close(1001)
            except WebSocketDisconnect:
                logger.info("Unauthenticated WebSocket disconnected.")
            except Exception as e:
                logger.error(f"Error in unauthenticated WebSocket handling: {e}")
                await websocket.close(1001)

        except WebSocketDisconnect:
            logger.debug("WebSocket disconnected")
            await websocket.close(1001)
        except Exception as e:
            logger.error(f"WebSocket connection error: {e}")
            await websocket.close(1001)

    # async def keep_alive(self, websocket: WebSocket):
    #     """ Periodically sends ping messages to prevent timeouts """
    #     try:
    #         while True:
    #             await asyncio.sleep(10)  # Adjust time as needed
    #             await websocket.send_text(json.dumps({"type": "ping"}))
    #     except Exception as e:
    #         print(f"Error sending keep-alive ping: {e}")

    async def disconnect_websocket(self, websocket: WebSocket):
        user_id = None
        for uid, conn in self.active_connections.items():
            if conn == websocket:
                user_id = uid
                break
        if user_id:
            try:
                await websocket.close(code=1001)
            except Exception:
                logger.warning(f"WebSocket for user {user_id} was already closed.")
            finally:
                self.active_connections.pop(user_id, None)
                logger.debug(f"Disconnected user {user_id} and removed from active connections.")

    def disconnect(self, user_id):
        self.active_connections[user_id].close(1001)
        del self.active_connections[user_id]

    async def send_personal_message(self, user_id, message: str):
        try:
            await self.active_connections[str(user_id)].send_text(message)
        except KeyError:
            logger.warning(f"User ID {user_id} not found in active connections.")
        except AttributeError:
            logger.error(f"Connection object for user ID {user_id} does not support send_text method.")
        except Exception as e:
            logger.error(f"An unexpected error occurred while sending message to user ID {user_id}: {str(e)}")

    async def broadcast(self, message: str):
        for user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(message)
            except Exception as Ex:
                logger.error("error", Ex)

    async def listen_for_messages(self, websocket: WebSocket, user_id: str):
        """Listen for incoming messages from the client"""
        logger.info(f"Start listen for incoming messages from the client.....")
        try:
            while True:
                message = await websocket.receive_text()
                if message != '{"action":"ping"}':
                    logger.info(f"Received message from user {user_id}: {message}")

                # Handle different types of messages
                try:
                    data = json.loads(message)
                    if "action" in data:
                        if data["action"] == "ping":
                            await websocket.send_text(json.dumps({"type": "pong"}))
                        if data["action"] == "watch" and "plural" in data.keys() and isinstance(data.get("plural"), str):
                            try:
                                await self.watch_user_resource(user_id=user_id, plural=data["plural"], namespace=config_app.k8s.velero_namespace)
                            except Exception as e:
                                logger.error(f"Error in watch_user_resource: {e}, user_id={user_id}, plural={data['plural']}, namespace={config_app.k8s.velero_namespace}")
                                if hasattr(self, 'watch_user_resource'):
                                    logger.watch("watch_user_resource exists")
                                else:
                                    logger.watch("watch_user_resource not exists")

                        if data["action"] == "watch:clear":
                            try:
                                await self.clear_watch_user_resource(user_id)
                            except Exception as e:
                                logger.error(f"Error in clear_watch_user_resource: {e}")

                        # elif data["action"] == "broadcast":
                        #     await self.broadcast(json.dumps({"message": data.get("message", "")}))
                        # elif data["action"] == "private_message":
                        #     target_user = data.get("target_user")
                        #     msg = data.get("message", "")
                        #     if target_user:
                        #         await self.send_personal_message(target_user, msg)

                    else:
                        logger.error("Invalid message format.")
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON message from user {user_id}: {message}")

        except WebSocketDisconnect:
            logger.warning(f"User {user_id} disconnected.")
            await self.disconnect_websocket(websocket)

        except Exception as e:
            logger.error(f"Error in listen_for_messages: {e}")
            await self.disconnect_websocket(websocket)

    # Global k8S Watch

    async def start_global_watch_tasks(self):
        """Launch the Global Watch for Common Resources"""
        if not self.watch_running:
            logger.watch("🟢 Starting Global Watch...")
            self.watch_running = True
            resources = ["backups", "restores", "serverstatusrequests", "downloadrequests", "deletebackuprequests"]

            # Start a task for each resource and keep them in the list
            self.watch_tasks = [asyncio.create_task(self.watch_velero_resource(resource, config_app.k8s.velero_namespace)) for resource in resources]

    async def stop_global_watch_tasks(self):
        """Stop all Global Watch."""
        if self.watch_running:
            logger.watch("🛑 Stopping Global Watch...")
            self.watch_running = False
            for task in self.watch_tasks:
                task.cancel()
            self.watch_tasks.clear()

    async def watch_velero_resource(self, plural, namespace):
        """Monitor a single Velero resource and send WebSocket notifications without blocking the loop"""
        # Load Kubernetes configuration
        try:
            config.load_incluster_config()
            # logger.info("Kubernetes in cluster mode....")
        except config.ConfigException:
            # Use local kubeconfig file if running locally
            await config.load_kube_config(config_file=config_app.k8s.kube_config)
            # logger.info("Kubernetes load local kube config...")

        crd_api = client.CustomObjectsApi()
        w = watch.Watch()

        try:
            # Get the latest version to avoid duplicate events
            response = await crd_api.list_namespaced_custom_object(
                group="velero.io",
                version="v1",
                namespace=namespace,
                plural=plural
            )
            last_resource_version = response.get("metadata", {}).get("resourceVersion")

            logger.watch(f"📌 Beginning monitoring of {plural} from resourceVersion: {last_resource_version}")

            while self.watch_running:
                try:
                    async for event in w.stream(
                            crd_api.list_namespaced_custom_object,
                            group='velero.io',
                            version='v1',
                            namespace=namespace,
                            plural=plural,
                            resource_version=last_resource_version,
                            timeout_seconds=10
                    ):
                        event_type = event["type"]
                        resource_name = event["object"]["metadata"]["name"]

                        # Update resourceVersion to avoid duplicate events
                        last_resource_version = event["object"]["metadata"]["resourceVersion"]

                        message = json.dumps({
                            "type": "global_watch",
                            "resources": plural,
                            "event_type": event_type,
                            "resource": event["object"]
                        })

                        logger.watch(f"📢 Event on {plural}: {message}")
                        await self.broadcast(message)

                except client.exceptions.ApiException as e:
                    if e.status == 410:  # ResourceVersion troppo vecchio
                        logger.watch(f"⚠️ ResourceVersion expired for {plural}, reset...")
                        # return await self.watch_velero_resource(plural, namespace)  # Riavvia il watch
                    else:
                        logger.error(f"❌ API error in the watch of {plural}: {e}")
                except Exception as e:
                    logger.error(f"⚠️ General error in the watch of {plural}: {e}")
                finally:
                    # TODO: check why it disconnects
                    # print(f"🔄 Reconnection to {plural} in 5 seconds...")
                    await asyncio.sleep(5)

        except Exception as e:
            logger.error(f"⚠️ Watch startup error for {plural}: {e}")

    # User k8s watch

    async def clear_watch_user_resource(self, user_id):
        """
        Stops and removes all active watches for a given user.
        """
        if user_id in self.user_watch_tasks:
            logger.watch(f"🛑 [{user_id}] Clearing all active watches...")
            for task in self.user_watch_tasks[user_id].values():
                task.cancel()
            del self.user_watch_tasks[user_id]
        else:
            logger.watch(f"ℹ️ [{user_id}] No active watches to clear.")

    async def watch_user_resource(self, user_id, plural, namespace):
        """
        Allows a user to watch multiple resources (plurals) simultaneously.

        📌 Each `plural` is watched separately, and a user can have multiple active watches.
        📌 If a user is already watching the requested resource type, the existing watch is not interrupted.
        """

        # 📌 Ensure that `plural` is provided
        if not plural:
            logger.watch(f"⚠️ [{user_id}] Error: `plural` parameter is required to start a watch.")
            return

        # Initialize user watch dictionary if it doesn't exist
        if user_id not in self.user_watch_tasks:
            self.user_watch_tasks[user_id] = {}

        # If the user is already watching this `plural`, do nothing
        if plural in self.user_watch_tasks[user_id]:
            logger.watch(f"ℹ️ [{user_id}] Already watching {plural}. No action taken.")
            return

        # 📌 Load Kubernetes configuration
        try:
            config.load_incluster_config()
            # logger.info("Kubernetes in cluster mode....")
        except config.ConfigException:
            # Use local kubeconfig file if running locally
            await config.load_kube_config(config_file=config_app.k8s.kube_config)
            # logger.info("Kubernetes load local kube config...")

        crd_api = client.CustomObjectsApi()
        w = watch.Watch()
        last_resource_version = None
        watch_target = f"all resources of type {plural}"

        try:
            # 📌 Get the latest resourceVersion to avoid duplicate events
            response = await crd_api.list_namespaced_custom_object(
                group="velero.io",
                version="v1",
                namespace=namespace,
                plural=plural
            )
            last_resource_version = response.get("metadata", {}).get("resourceVersion")

            logger.watch(f"📌 [{user_id}] Starting watch for {watch_target} from resourceVersion: {last_resource_version}")

        except client.exceptions.ApiException as e:
            logger.watch(f"⚠️ [{user_id}] Error fetching resourceVersion for {watch_target}: {e}")
            return
        except Exception as e:
            logger.watch(f"⚠️ [{user_id}] Unexpected error while fetching resourceVersion: {e}")
            return

        async def user_watch():
            """Watches the selected resource type and sends updates to the user via WebSocket."""
            nonlocal last_resource_version

            while user_id in self.active_connections:
                try:
                    async for event in w.stream(
                            crd_api.list_namespaced_custom_object,
                            group="velero.io",
                            version="v1",
                            namespace=namespace,
                            plural=plural,
                            resource_version=last_resource_version,
                            timeout_seconds=10
                    ):
                        event_type = event["type"]
                        event_resource = event["object"]

                        # 🔄 Update resourceVersion to avoid processing old events
                        last_resource_version = event_resource["metadata"]["resourceVersion"]

                        message = json.dumps({
                            "type": "user_watch",
                            "resources": plural,
                            "event_type": event_type,
                            "resource": event_resource
                        })

                        logger.watch(f"📢 [{user_id}] New event: {message}")
                        await self.send_personal_message(user_id, message)

                except client.exceptions.ApiException as e:
                    if e.status == 410:  # ResourceVersion too old, reset the watch
                        logger.error(f"⚠️ [{user_id}] ResourceVersion expired for {watch_target}, restarting watch...")
                        return await self.watch_user_resource(user_id, plural=plural, namespace=namespace)
                    else:
                        logger.error(f"❌ [{user_id}] API Error in watch for {watch_target}: {e}")
                except Exception as e:
                    logger.error(f"⚠️ [{user_id}] General error in watch for {watch_target}: {e}")
                finally:
                    # TODO: check why it disconnects
                    # print(f"🔄 [{user_id}] Reconnecting to {watch_target} in 5 seconds...")
                    await asyncio.sleep(5)

        # 📌 Start the watch as a separate async task and store it in the user's watch list
        self.user_watch_tasks[user_id][plural] = asyncio.create_task(user_watch())

        logger.info(f"✅ [{user_id}] Now watching {plural}.")


manager = WebSocketManager()

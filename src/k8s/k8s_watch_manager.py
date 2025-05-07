import asyncio
import json
from datetime import datetime

from kubernetes_asyncio import client, config, watch
from vui_common.logger.logger_proxy import logger
from vui_common.configs.config_proxy import config_app


class K8sWatchManager:
    def __init__(self, send_global_callback, send_user_callback):
        self.watch_running = False
        self.watch_tasks = []
        self.user_watch_tasks = {}

        self.send_global_message = send_global_callback
        self.send_user_message = send_user_callback

    async def start_global_watch_tasks(self):
        """Launch the Global Watch for Common Resources"""
        if not self.watch_running:
            logger.watch("🟢 Starting Global Watch...")
            self.watch_running = True
            resources = ["backups", "restores", "serverstatusrequests", "downloadrequests", "deletebackuprequests"]

            # Start a task for each resource and keep them in the list
            self.watch_tasks = [
                asyncio.create_task(self.watch_velero_resource(resource, config_app.k8s.velero_namespace)) for resource
                in resources]

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
                            "kind": "event",
                            "payload": {
                                "resources": plural,
                                "resource": event["object"]
                            },
                            'timestamp': datetime.utcnow().isoformat(),
                            'agent_name': config_app.k8s.cluster_id
                        })

                        logger.watch(f"📢 Event on {plural}: {message}")
                        # await self.broadcast(message)
                        await self.send_global_message(message)

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

            logger.watch(
                f"📌 [{user_id}] Starting watch for {watch_target} from resourceVersion: {last_resource_version}")

        except client.exceptions.ApiException as e:
            logger.watch(f"⚠️ [{user_id}] Error fetching resourceVersion for {watch_target}: {e}")
            return
        except Exception as e:
            logger.watch(f"⚠️ [{user_id}] Unexpected error while fetching resourceVersion: {e}")
            return

        async def user_watch():
            """Watches the selected resource type and sends updates to the user via WebSocket."""
            nonlocal last_resource_version

            # while user_id in self.active_connections:
            while True:
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
                            "kind": "event",
                            "payload": {
                                "resources": plural,
                                "event_type": event_type,
                                "resource": event_resource
                            },
                            'timestamp': datetime.utcnow().isoformat(),
                            'agent_name': config_app.k8s.cluster_id
                        })

                        logger.watch(f"📢 [{user_id}] New event: {message}")
                        # await self.send_personal_message(user_id, message)
                        await self.send_user_message(user_id, message)

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

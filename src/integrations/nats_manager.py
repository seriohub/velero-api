from datetime import datetime
import socket
import os
from fastapi import FastAPI, Request
from fastapi.routing import APIRoute, Mount
from fastapi.responses import JSONResponse
from nats.js.api import KeyValueConfig
from pydantic import BaseModel
from inspect import signature

import asyncio
import json

import nats
from nats.aio.errors import ErrTimeout, ErrNoServers
from nats.errors import NoRespondersError

from integrations.nats_cron_jobs import NatsCronJobs
from vui_common.models.db.user import User

from vui_common.contexts.context import current_user_var, cp_user
from vui_common.configs.config_proxy import config_app

from vui_common.logger.logger_proxy import logger

from k8s import k8s_watcher_proxy

class NatsManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(NatsManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, app):
        self.app = app
        self.nc = None
        self.js = None

        self.kv_bucket_name = f"kv-{config_app.k8s.cluster_id}"

        self.kv_job_cron = NatsCronJobs()
        self.channel_id = config_app.k8s.cluster_id

        self.retry_registration_sec = config_app.nats.retry_registration
        self.alive_sec = config_app.nats.send_alive
        self.timeout_request = config_app.nats.timeout_request

    def __ensure_encoded(self, data):
        """
        Ensures that the given data is encoded in bytes. If it's already encoded,
        it returns the data as is. If not, it encodes the data.
        """
        logger.debug(f"__ensure_encoded")
        if isinstance(data, bytes):
            # Data is already encoded
            return data
        elif isinstance(data, str):
            # Data is a string, encode it to bytes
            return data.encode()
        else:
            # Data is not a string, convert to JSON string and encode to bytes
            return json.dumps(data).encode()

    # ------------------------------------------------------------------------------------------------
    #             NATS CONNECTION CALLBACK
    # ------------------------------------------------------------------------------------------------

    async def __error_cb(self, e):
        logger.error(f"_nats_error_cb {str(e)}")

    async def __closed_cb(self):
        logger.info(f"_nats_closed_cb")

    async def __reconnected_cb(self):
        logger.info(f"_nats_reconnect reconnect at {self.nc.connected_url.netloc}")
        await self.__start_manager()
        #await self.__init_nats_connection()
        #await self.__agent_registration()
        #await self.__create_bucket_store(key_value=self.kv_bucket_name)
        #await self.__subscribe_to_nats()

    async def __disconnected_cb(self):
        logger.info(f"_nats_disconnected_cb disconnect from server")

    # ------------------------------------------------------------------------------------------------
    #             NATS CONNECTION UTILS
    # ------------------------------------------------------------------------------------------------

    async def __start_manager(self):
        await self.__init_nats_connection()
        await self.__agent_registration()
        await self.__create_bucket_store(key_value=self.kv_bucket_name)
        await self.__subscribe_to_nats()

    async def __init_nats_connection(self):
        try:
            logger.info(f"__init_nats_connection")
            if self.nc is not None and self.nc.is_connected:
                logger.info("[NATS] Already connected.")
                return
            else:
                nats_server = f"{config_app.nats.nats_client_url}"
                reconnect_sec = config_app.nats.retry_connection
                if reconnect_sec < 10:
                    reconnect_sec = 10
                logger.info(f"Connect to server: {nats_server}- timeout reconnect: {reconnect_sec} sec")

                worker_id = f"{socket.gethostname()}-{os.getpid()}"
                options = {
                    "name": f"Agent.{config_app.k8s.cluster_id}.{worker_id}",
                    "servers": [nats_server],
                    "error_cb": self.__error_cb,
                    "closed_cb": self.__closed_cb,
                    "reconnected_cb": self.__reconnected_cb,
                    "disconnected_cb": self.__disconnected_cb,
                    "reconnect_time_wait": reconnect_sec
                }

                self.nc = await nats.connect(**options)
                self.js = self.nc.jetstream()
        except Exception as e:
            logger.warning(f"__init_nats_connection ({str(e)})")
            self.nc = None

    async def __create_bucket_store(self, key_value, max_size=16777216):
        logger.info(f"create_bucket_store {key_value} ")
        self.js = self.nc.jetstream()
        bucket_name = f"{key_value}"
        interval = 2
        exists = False

        # Check if the KV store exists and delete it if it does
        try:
            await self.js.stream_info(bucket_name)
            logger.debug(f"create_bucket_store.{bucket_name} store exists.")
            exists = True
            # await self.js.delete_key_value(bucket_name)
        except Exception as e:
            logger.debug(f"create_bucket_store.KV {bucket_name} store does not exist or cannot be retrieved. {str(e)}")

        is_not_created = False
        if not exists:
            while not is_not_created:
                try:
                    # Create a KV store
                    kv_config = KeyValueConfig(
                        bucket=bucket_name,
                        max_value_size=max_size,
                        history=1  # Only keep the latest value
                    )
                    await self.js.create_key_value(kv_config)

                    logger.info(f"create_bucket_store.{bucket_name} store created.")
                    is_not_created = True
                except Exception as e:
                    logger.debug(f"create_bucket_store. {bucket_name} cannot create the kv. {str(e)}")
                finally:
                    if is_not_created:
                        return True
                    else:
                        await asyncio.sleep(interval)

        return True

    # ------------------------------------------------------------------------------------------------
    #             NATS CONNECTIONS
    # ------------------------------------------------------------------------------------------------

    # async def connect(self):
    #     try:
    #         logger.info(f"get_nats_connection")
    #         if self.nc is None:
    #             await self.__init_nats_connection()
    #         logger.info(f"Nast connection: Status: {self.nc.is_connected} - client id {self.nc.client_id}")
    #
    #         return self.nc
    #
    #     except Exception as e:
    #         logger.warning(f"get_nats_connection ({str(e)})")
    #         self.nc = None
    #         return None

    # async def __agent_registration(self):
    #     logger.info(f"__agent_registration: name={config_app.k8s.cluster_id} client_id={self.nc.client_id}")
    #     connected = False
    #     attempt = 0
    #     interval = self.retry_registration_sec  # seconds to wait
    #
    #     while not connected:
    #         try:
    #             if not self.nc.is_connected:
    #                 logger.warning("⛔ NATS not connected, retrying...")
    #                 await asyncio.sleep(interval)
    #                 continue
    #
    #             try:
    #                 subject = f"register.client2.{self.nc.client_id}"
    #                 responders = await self.nc.responder_count(subject)
    #
    #                 if responders == 0:
    #                     logger.debug("No responders yet, skipping request.")
    #                     await asyncio.sleep(interval)
    #                     continue
    #             except Exception as e:
    #                 logger.debug(f"responder_count check failed: {e}")
    #
    #             attempt += 1
    #             data = {'client': self.nc.client_id, 'name': config_app.k8s.cluster_id}
    #             # Convert the dictionary to a JSON string
    #             message = json.dumps(data)
    #             # Request-reply pattern
    #             logger.info(f"registration.sent attempt={attempt}")
    #             response = await self.nc.request(f"register.client.{self.nc.client_id}",
    #                                              message.encode('utf-8'), timeout=2)
    #             key_to_res = response.data.decode()
    #             logger.debug(f"command.Received reply: {key_to_res}")
    #
    #             res = json.loads(key_to_res)
    #             if res.get("registered") in ("ok!", True):
    #                 connected = True
    #             else:
    #                 logger.warning(f"Unexpected registration response: {res}")
    #
    #         except ErrTimeout as e:
    #             logger.warning(f"No reply received (timeout)-{str(e)}")
    #         except ErrNoServers as e:
    #             logger.warning(f"No reply received (no-server)-{str(e)}")
    #         except NoRespondersError as e:
    #             logger.warning(f"No responders available for request-{str(e)}")
    #         except Exception as e:
    #             logger.warning(f"No reply received ({str(e)})")
    #
    #         if not connected:
    #             await asyncio.sleep(interval)
    #
    #     return connected

    async def __agent_registration(self):
        logger.info(f"__agent_registration: name={config_app.k8s.cluster_id} client_id={self.nc.client_id}")

        connected = False
        attempt = 0
        interval = self.retry_registration_sec  # seconds to wait

        while not connected:
            try:
                if not self.nc.is_connected:
                    logger.warning("⛔ NATS not connected, retrying...")
                    await asyncio.sleep(interval)
                    break

                data = {
                    'client': self.nc.client_id,
                    'name': config_app.k8s.cluster_id
                }
                message = json.dumps(data)

                subject = f"register.client.{self.nc.client_id}"
                attempt += 1
                logger.info(f"📤 registration.sent attempt={attempt} → {subject}")

                # Request/Reply
                response = await self.nc.request(subject, message.encode(), timeout=5)
                print("response", response)
                key_to_res = response.data.decode()
                logger.debug(f"📥 command.Received reply: {key_to_res}")

                res = json.loads(key_to_res)
                if res.get("registered") in ("ok!", True):
                    logger.info("✅ Registration successful!")
                    connected = True
                else:
                    logger.warning(f"⚠️ Unexpected registration response: {res}")

            except NoRespondersError:
                logger.warning("⚠️ No responders available. Will retry...")
            except ErrTimeout:
                logger.warning("⏳ Timeout waiting for reply. Retrying...")
            except ErrNoServers:
                logger.warning("🚫 No NATS server available.")
            except Exception as e:
                logger.warning(f"❌ Unknown error during registration: {e}")

            if not connected:
                await asyncio.sleep(interval)

        return connected

    async def __send_client_alive(self):
        subject = f"status.client.{self.channel_id}"
        interval = self.alive_sec

        await asyncio.sleep(interval)
        while True:
            try:
                if self.nc and self.nc.is_connected:
                    message = json.dumps({
                        'client': self.nc.client_id,
                        'name': config_app.k8s.cluster_id,
                        'status': 'alive',
                        'timestamp': datetime.utcnow().isoformat()
                    })
                    logger.debug(f"alive message {subject}: {message}")
                    response = await self.nc.request(subject, message.encode(), timeout=self.timeout_request)
                    logger.debug(f"__send_client_alive Received reply: {response.data.decode()}")
                else:
                    logger.warning("__send_client_alive: NATS not connected.")
            except ErrTimeout:
                logger.warning("__send_client_alive No reply received from server (timeout)")
            except ErrNoServers:
                logger.warning("__send_client_alive No reply received (no nats server)")
            except Exception as e:
                logger.warning(f"__send_client_alive ({str(e)})")
            finally:
                await asyncio.sleep(interval)  # Publish every x seconds

    # ------------------------------------------------------------------------------------------------
    #             KEY VALUE JETSTREAM DATA
    # ------------------------------------------------------------------------------------------------

    @staticmethod
    def __get_endpoint_function_by_path(app_fastapi: FastAPI, path: str, method:str, debug=False):
        # Helper function to search routes
        def search_routes(routes, path, method):
            for route in routes:
                if isinstance(route, APIRoute):
                    if debug:
                        print(f"route: {route.path} - methods: {route.methods} - find: {path} [{method}]")
                    if route.path == path and method.upper() in route.methods:
                        return route.endpoint
                elif isinstance(route, Mount):
                    if debug:
                        print(f"route mount:{route}-find:{path}")
                    # Check mounted sub-application routes
                    sub_app = route.app
                    if debug:
                        print(f"route:{route}-sun_app:{sub_app}-find:{path}")
                    sub_path = path[len(route.path.rstrip("/")):]
                    if sub_path:
                        if debug:
                            print(f"sub_path:{route}-sun_app:{sub_app}-find:{path}")
                        sub_endpoint = search_routes(sub_app.routes, sub_path, method)
                        if sub_endpoint:
                            return sub_endpoint
                else:
                    if debug:
                        print(f"no found type:{route}")
            return None

        return search_routes(app_fastapi.routes, path, method)

    # ------------------------------------------------------------------------------------------------
    #             API UTILS
    # ------------------------------------------------------------------------------------------------

    async def __get_data_from_api(self, path, method, credential: bool = False):

        logger.debug(f"__get_data_from_api {path}")
        try:
            if credential:
                # create temp user
                user = User()
                user.username = "nats"
                user.is_nats = True
                user.cp_mapping_user = 'local-nats'
                current_user_var.set(user)
                cp_user.set("local-nats")

            endpoint_function = self.__get_endpoint_function_by_path(self.app, path, method)
            response = await endpoint_function()

            if isinstance(response, JSONResponse):
                return json.loads(response.body.decode())

            return response
        except Exception as e:
            logger.warning(f"__get_data_from_api ({str(e)})")
            return None

    # def __query_string_to_dict(self, query_string: str) -> dict:
    #     from urllib.parse import parse_qs
    #     query_dict = parse_qs(query_string)
    #     return {k: v[0] for k, v in query_dict.items()}
    def __query_string_to_dict(self, query_string: str) -> dict:
        from urllib.parse import parse_qs

        def convert(value: str):
            lowered = value.lower()
            if lowered in ["true", "false"]:
                return lowered == "true"
            try:
                return json.loads(value)
            except Exception:
                return value

        query_dict = parse_qs(query_string)
        return {k: convert(v[0]) for k, v in query_dict.items()}

    # ------------------------------------------------------------------------------------------------
    #             SUBSCRIBE AND CALLBACK
    # ------------------------------------------------------------------------------------------------

    async def __subscribe_to_nats(self):
        logger.debug(f"initialize nats subscriptions")
        await self.nc.subscribe(f"agent.{config_app.k8s.cluster_id}.online", cb=self.__online_handler_cb)
        await self.nc.subscribe(f"agent.{config_app.k8s.cluster_id}.request", cb=self.__api_handler_cb)
        await self.nc.subscribe(f"server.cmd", cb=self.__server_cmd_cb)
        await self.nc.subscribe(f"event.user.watch.{self.channel_id}", cb=self.__k8s_user_wacth_cb)

    async def __online_handler_cb(self, msg):
        logger.debug(f"reply to online check request")
        data = {'online': True}
        content = json.dumps(data)
        await self.nc.publish(msg.reply, self.__ensure_encoded(content))

    async def __api_handler_cb(self, msg):
        logger.info(f"message_handler")
        command = msg.data.decode()

        logger.debug(f"message_handler:{command}")

        if command:
            command = json.loads(command)
        else:
            await self.nc.publish(msg.reply, "error".encode())
        logger.debug(f"message_handle.command {command['method']} \tpath:{command['path']} ")
        # path = "/api/info/get"
        endpoint_function = self.__get_endpoint_function_by_path(self.app, command['path'], command['method'])

        if endpoint_function is not None:
            logger.debug(f"message_handle.endpoint_function is ok ")

            # access_token = create_access_token(
            #     data={'sub': 'nats', 'is_nats': True}
            # )

            commands = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']

            # create temp user
            user = User()
            user.username = "nats"
            user.is_nats = True
            user.cp_mapping_user = command["user"]
            current_user_var.set(user)
            cp_user.set(command["user"])
            response = {}

            if command['method'] in commands:

                if command['method'] == 'GET':
                    logger.debug(f"message_handle.command {command['method']}")

                    # Call endpoint function with TestClient
                    # response = TestClient(self.app).get(command['path'],
                    #                                     params=command['params'],
                    #                                     headers={"Authorization": f"Bearer {access_token}",
                    #                                              "cp_user": command["user"]})

                    if 'params' in command and len(command['params']) > 0:
                        query_dict = self.__query_string_to_dict(command['params'])
                        response = await endpoint_function(**query_dict)
                    else:
                        response = await endpoint_function()

                    if isinstance(response, JSONResponse):
                        response = json.loads(response.body.decode())

                elif command['method'] == 'POST' or command['method'] == 'PATCH' or command['method'] == 'PUT' or command['method'] == 'DELETE':
                    logger.debug(f"message_handle.command {command['method']}")

                    # Call endpoint function with TestClient
                    # response = TestClient(self.app).post(command['path'],
                    #                                      json=command['params'],
                    #                                      headers={"Authorization": f"Bearer {access_token}",
                    #                                               "cp_user": command["user"]})

                    # get function signature
                    sig = signature(endpoint_function)

                    params = list(sig.parameters.values())

                    if not params:
                        response = await endpoint_function()
                    else:
                        first_param = next(iter(sig.parameters.values()))
                        # get first param of endpoint
                        if first_param.annotation == Request:
                            # Create fake Request Object
                            request_scope = {
                                "type": "http",
                                "method": command['method'],
                                "path": command["path"],
                                "headers": {},
                            }
                            request = Request(request_scope)
                            request._json = command['params']

                            # call endpoint with Request object
                            response = await endpoint_function(request)
                        elif issubclass(first_param.annotation, BaseModel):
                            # Create Pydantic schemas
                            model_instance = first_param.annotation(**command['params'])
                            # call endpoint with Pydantic object
                            response = await endpoint_function(model_instance)
                        # else:
                        #     raise HTTPException(status_code=400, detail="Unsupported parameter type")

                        # If the response is a JSONResponse object, get content
                        if isinstance(response, JSONResponse):
                            response = json.loads(response.body.decode())

                content = json.dumps(response)

            else:  # command['method'] not in commands:
                logger.warning(f"message_handle.command {command['method']} not recognized ")
                data = {'success': False, 'error': {'title': 'message_handler',
                                                    'description': f"Method not recognized {command['method']}"
                                                    }
                        }
                content = json.dumps(data)
                logger.warning(f"message_handler:{content}")
        else:  # endpoint_function is None
            data = {'success': False, 'error': {'title': 'message_handler',
                                                'description': f"No endpoint found for path: {command['path']}"
                                                }
                    }
            content = json.dumps(data)

            logger.warning(f"message_handler:{content}")

        await self.nc.publish(msg.reply, self.__ensure_encoded(content))

    async def __k8s_user_wacth_cb(self, msg):
        command = msg.data.decode()
        command = json.loads(command)
        logger.info(f"k8s_user_watch {msg} {command.get('type')}")
        if command.get('type') == "watch":
            if k8s_watcher_proxy.k8s_watcher_manager is not None:
                await k8s_watcher_proxy.k8s_watcher_manager.watch_user_resource(-1, command.get("payload").get('plural'), namespace=config_app.k8s.velero_namespace)
            else:
                print("is none")
        if command.get('type') == "watch_clear":
            if k8s_watcher_proxy.k8s_watcher_manager is not None:
                await k8s_watcher_proxy.k8s_watcher_manager.clear_watch_user_resource(-1)
            else:
                print("is none")

    async def __server_cmd_cb(self, msg):
        try:
            logger.debug(f"cmd from server")
            command = msg.data.decode()
            logger.debug(f"cmd from server. command : {command}")

            if command:
                command = json.loads(command)
                logger.debug(f"force registration and subscription")
                if command['command'] == 'restart':
                    await self.__agent_registration()

        except Exception as e:
            logger.warning(f"__server_cmd_handler ({str(e)})")

    # ------------------------------------------------------------------------------------------------
    #             PUBLISH CRON KEY VALUE IN JETSTREAM
    # ------------------------------------------------------------------------------------------------

    async def __publish_kv_pair(self, key, value):
        try:
            logger.debug(f"__publish_kv_pair.key {key}")
            if self.nc is not None:
                js = self.nc.jetstream()
                kv = await js.key_value(self.kv_bucket_name)

                data = self.__ensure_encoded(value)

                # await kv.put(key, json.dumps(value).encode())
                await kv.put(key, data)
                logger.debug(f"__publish_kv_pair.published {key}")
                return True
            else:
                logger.warning("nats connections is not ready")

        except ErrTimeout:
            logger.warning("__publish_kv_pair No reply received from server (timeout)")
        except ErrNoServers:
            logger.warning("__publish_kv_pair No reply received (no nats server)")
        except Exception as e:
            logger.warning(f"__publish_kv_pair ({str(e)})")

        return False

    async def __publish_data_to_kv(self):
        logger.info(f"__publish_data_to_kv.client {self.kv_bucket_name}")
        interval = 1
        self.kv_job_cron.print_info()

        while True:
            try:
                self.kv_job_cron.add_tick_to_interval(1)
                for name, job in self.kv_job_cron.jobs.items():
                    if job.is_elapsed:
                        logger.debug(f"__publish_data_to_kv. batch {name}")
                        job.reset_timer()
                        data = await self.__get_data_from_api(path=job.endpoint, credential=job.credential, method="GET")
                        if data is not None:
                            logger.info(f"set kv in jetstream {job.ky_key} {str(data)[:100]}...")
                            if isinstance(data, dict):
                                data['metadata'] = {
                                    'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                                    'source': 'cron job'
                                }
                            else:
                                logger.warning(f"Unexpected data format: {type(data)} - {str(data)[:100]}")

                            update = await self.__publish_kv_pair(key=job.ky_key, value=data)

                            logger.info(f"__publish_data_to_kv. update {job.ky_key} res: {update}")

            except ErrTimeout:
                logger.error("__publish_data_to_kv No reply received from server (timeout)")
            except ErrNoServers:
                logger.error("__publish_data_to_kv No reply received (no nats server)")
            except Exception as e:
                logger.error(f"__publish_data_to_kv ({str(e)})")
            finally:
                await asyncio.sleep(interval)  # Publish every x seconds

    # ------------------------------------------------------------------------------------------------
    #             PUBLISH
    # ------------------------------------------------------------------------------------------------

    async def publish_global_event(self, message: str):
        """
        Pubblica un evento globale (ad es. da K8sWatchManager) su un canale NATS pubblico.
        """
        try:
            # if self.nc is None or not self.nc.is_connected:
            #     await self.connect()

            subject = f"event.global.{self.channel_id}"
            payload = self.__ensure_encoded(message)

            await self.nc.publish(subject, payload)
            logger.debug(f"📡 publish_global_event sent to {subject}: {message}")
        except Exception as e:
            logger.warning(f"❌ Error in publish_global_event: {e}")

    async def publish_user_event(self, cluster: str, message: str):
        """
        Pubblica un evento globale (ad es. da K8sWatchManager) su un canale NATS pubblico.
        """
        try:
            # if self.nc is None or not self.nc.is_connected:
            #    await self.connect()

            subject = f"event.global.{self.channel_id}"
            payload = self.__ensure_encoded(message)

            await self.nc.publish(subject, payload)
            logger.debug(f"📡 publish_global_event sent to {subject}: {message}")
        except Exception as e:
            logger.warning(f"❌ Error in publish_global_event: {e}")

    # ------------------------------------------------------------------------------------------------
    #             RUN
    # ------------------------------------------------------------------------------------------------

    async def run(self):
        await self.__start_manager()

        # Create a task to publish messages at intervals
        publish_status = asyncio.create_task(self.__send_client_alive())
        await asyncio.sleep(5)
        # Create a task to publish status to kv value at intervals
        publish_kv_status = asyncio.create_task(self.__publish_data_to_kv())

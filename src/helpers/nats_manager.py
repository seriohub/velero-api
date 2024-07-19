from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.routing import APIRoute, Mount
from fastapi.responses import JSONResponse
from nats.js.api import StreamConfig, KeyValueConfig
from pydantic import BaseModel
from inspect import signature

import asyncio
import json

import nats
from nats.aio.errors import ErrTimeout, ErrNoServers
from nats.errors import NoRespondersError

from helpers.nats_cron_jobs import NatsCronJobs
from security.helpers.database import User

from helpers.printer import PrintHelper

from core.context import current_user_var, cp_user
from core.config import ConfigHelper

# from fastapi.testclient import TestClient


config = ConfigHelper()


class NatsManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(NatsManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, app):
        self.print_ls = PrintHelper('[helpers.nast_manager]',
                                    level=config.get_internal_log_level())

        self.app = app
        self.nc = None
        self.js = None

        self.kv_bucket_name = f"kv-{config.cluster_id()}"

        # self.kv_stats_path = "/api/v1/stats/get"
        # self.kv_stats_name = 'stast_get'
        # self.kv_stats_interval = config.get_nats_update_sec_statistic()
        #
        # self.kv_health_path = "/api/info/health-k8s"
        # self.kv_health_k8s_name = 'k8s_health'
        # self.kv_health_k8s_interval = config.get_nats_update_sec_k8s_health()
        self.kv_job_cron = NatsCronJobs()

        self.channel_id = config.cluster_id()
        self.retry_registration_sec = config.get_nast_retry_registration()
        self.alive_sec = config.get_nast_send_alive()
        self.timeout_request = config.get_timeout_request()

    async def __nats_error_cb(self, e):
        self.print_ls.wrn(f"_nats_error_cb {e}")

    async def __nats_closed_cb(self):
        self.print_ls.info(f"_nats_closed_cb")

    async def __nats_reconnected_cb(self):
        self.print_ls.info(f"_nats_reconnect reconnect at {self.nc.connected_url.netloc}")
        self.print_ls.debug(f"run.registration")
        await self.client_registration()

    async def __nats_disconnected_cb(self):
        self.print_ls.info(f"_nats_disconnected_cb disconnect from server")

    async def __init_nats_connection(self):
        try:
            self.print_ls.info(f"__init_nats_connection")
            if self.nc is None:
                nats_server = f"{config.get_nats_client_url()}"
                reconnect_sec = config.get_nast_retry_connection()
                if reconnect_sec < 10:
                    reconnect_sec = 10
                self.print_ls.info(f"Connect to server: {nats_server}- timeout reconnect: {reconnect_sec} sec")

                options = {
                    "name": "AgentAPI." + config.cluster_id(),
                    "servers": [nats_server],
                    "error_cb": self.__nats_error_cb,
                    "closed_cb": self.__nats_closed_cb,
                    "reconnected_cb": self.__nats_reconnected_cb,
                    "disconnected_cb": self.__nats_disconnected_cb,
                    "reconnect_time_wait": reconnect_sec
                }

                self.nc = await nats.connect(**options)
        except Exception as e:
            self.print_ls.wrn(f"__init_nats_connection ({str(e)})")
            self.nc = None

    def __ensure_encoded(self, data):
        """
        Ensures that the given data is encoded in bytes. If it's already encoded,
        it returns the data as is. If not, it encodes the data.
        """
        self.print_ls.trace(f"__ensure_encoded")
        if isinstance(data, bytes):
            # Data is already encoded
            return data
        elif isinstance(data, str):
            # Data is a string, encode it to bytes
            return data.encode()
        else:
            # Data is not a string, convert to JSON string and encode to bytes
            return json.dumps(data).encode()

    async def create_bucket_store(self, key_value, max_size=500000):
        self.print_ls.info(f"create_bucket_store {key_value} ")
        self.js = self.nc.jetstream()
        bucket_name = f"{key_value}"
        interval = 2
        # Check if the KV store exists and delete it if it does
        try:
            await self.js.stream_info(bucket_name)
            self.print_ls.debug(f"create_bucket_store.{bucket_name} store exists. Deleting...")
            await self.js.delete_key_value(bucket_name)
        except Exception as e:
            self.print_ls.debug(f"create_bucket_store.KV {bucket_name} store does not exist or cannot be retrieved.")
        is_not_created = False
        while not is_not_created:
            try:
                # Create a KV store
                kv_config = KeyValueConfig(
                    bucket=bucket_name,
                    max_value_size=max_size,
                    history=1  # Only keep the latest value
                )
                await self.js.create_key_value(kv_config)

                self.print_ls.info(f"create_bucket_store.{bucket_name} store created.")
                is_not_created = True
            except Exception as e:
                self.print_ls.debug(f"create_bucket_store. {bucket_name} cannot create the kv")
            finally:
                if is_not_created:
                    return True
                else:
                    await asyncio.sleep(interval)
        return True

    async def client_registration(self):
        self.print_ls.info(f"__init_client_register")
        connected = False
        in_error = False
        attempt = 0
        interval = self.retry_registration_sec  # seconds to wait
        while not connected and not in_error:
            try:
                attempt += 1
                data = {'client': self.nc.client_id, 'name': config.cluster_id()}
                # Convert the dictionary to a JSON string
                message = json.dumps(data)
                # Request-reply pattern
                self.print_ls.info(f"registration.sent attempt={attempt}")
                response = await self.nc.request(f"register.client.{self.nc.client_id}",
                                                 message.encode('utf-8'), timeout=2)
                key_to_res = response.data.decode()
                self.print_ls.debug(f"command.Received reply: {key_to_res}")

                if "registered" in key_to_res:
                    self.print_ls.debug(f"client ready to receive message ")
                    connected = True
                else:
                    self.print_ls.wrn(f"try to register to nats server")

            except ErrTimeout as e:
                self.print_ls.wrn(f"No reply received (timeout)-{str(e)}")
            except ErrNoServers as e:
                self.print_ls.wrn(f"No reply received (no-server)-{str(e)}")
                in_error = True
            except NoRespondersError as e:
                self.print_ls.wrn(f"No responders available for request-{str(e)}")
            except Exception as e:
                in_error = True
                self.print_ls.wrn(f"No reply received ({str(e)})")

            if not connected:
                await asyncio.sleep(interval)

        return connected

    async def get_nats_connection(self):
        try:
            self.print_ls.info(f"get_nats_connection")
            if self.nc is None:
                await self.__init_nats_connection()
            self.print_ls.info(f"Nast connection: Status: {self.nc.is_connected} - client id {self.nc.client_id}")

            return self.nc

        except Exception as e:
            self.print_ls.wrn(f"get_nats_connection ({str(e)})")
            self.nc = None
            return None

    @staticmethod
    def __get_endpoint_function_by_path(app_fastapi: FastAPI, path: str, debug=False):
        # Helper function to search routes
        def search_routes(routes, path):
            for route in routes:
                if isinstance(route, APIRoute):
                    if debug:
                        print(f"route:{route}-find:{path}")
                    if route.path == path:
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
                        sub_endpoint = search_routes(sub_app.routes, sub_path)
                        if sub_endpoint:
                            return sub_endpoint
                else:
                    if debug:
                        print(f"no found type:{route}")
            return None

        return search_routes(app_fastapi.routes, path)

    def query_string_to_dict(self, query_string: str) -> dict:
        from urllib.parse import parse_qs
        query_dict = parse_qs(query_string)
        return {k: v[0] for k, v in query_dict.items()}

    async def message_handler(self, msg):
        self.print_ls.info(f"message_handler")
        command = msg.data.decode()

        self.print_ls.trace(f"message_handler:{command}")

        if command:
            command = json.loads(command)
        else:
            await self.nc.publish(msg.reply, "error".encode())
        self.print_ls.trace(f"message_handle.command {command['method']} \tpath:{command['path']} ")
        # path = "/api/info/get"
        endpoint_function = self.__get_endpoint_function_by_path(self.app, command['path'])

        if endpoint_function is not None:
            self.print_ls.trace(f"message_handle.endpoint_function is ok ")

            # access_token = create_access_token(
            #     data={'sub': 'nats', 'is_nats': True}
            # )

            commands = ['GET', 'POST', 'DELETE']

            # create temp user
            user = User()
            user.username = "nats"
            user.is_nats = True
            user.cp_mapping_user = command["user"]
            current_user_var.set(user)
            cp_user.set(command["user"])
            response = {}

            if command['method'] in commands:

                if command['method'] == 'GET' or command['method'] == 'DELETE':
                    self.print_ls.trace(f"message_handle.command {command['method']}")

                    # Call endpoint function with TestClient
                    # response = TestClient(self.app).get(command['path'],
                    #                                     params=command['params'],
                    #                                     headers={"Authorization": f"Bearer {access_token}",
                    #                                              "cp_user": command["user"]})

                    if 'params' in command and len(command['params']) > 0:
                        query_dict = self.query_string_to_dict(command['params'])
                        response = await endpoint_function(**query_dict)
                    else:
                        response = await endpoint_function()

                    if isinstance(response, JSONResponse):
                        response = json.loads(response.body.decode())

                elif command['method'] == 'POST' or command['method'] == 'PATCH':
                    self.print_ls.trace(f"message_handle.command POST")

                    # Call endpoint function with TestClient
                    # response = TestClient(self.app).post(command['path'],
                    #                                      json=command['params'],
                    #                                      headers={"Authorization": f"Bearer {access_token}",
                    #                                               "cp_user": command["user"]})

                    # get function signature
                    sig = signature(endpoint_function)
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
                        # Create Pydantic model
                        model_instance = first_param.annotation(**command['params'])
                        # call endpoint with Pydantic object
                        response = await endpoint_function(model_instance)
                    # else:
                    #     raise HTTPException(status_code=400, detail="Unsupported parameter type")

                    # Se la risposta è un oggetto JSONResponse, get contenuto
                    if isinstance(response, JSONResponse):
                        response = json.loads(response.body.decode())

                content = json.dumps(response)

            else:  # command['method'] not in commands:
                self.print_ls.wrn(f"message_handle.command {command['method']} not recognized ")
                data = {'success': False, 'error': {'title': 'message_handler',
                                                    'description': f"Method not recognized {command['method']}"
                                                    }
                        }
                content = json.dumps(data)
                self.print_ls.wrn(f"message_handler:{content}")
        else:  # endpoint_function is None
            data = {'success': False, 'error': {'title': 'message_handler',
                                                'description': f"No endpoint found for path: {command['path']}"
                                                }
                    }
            content = json.dumps(data)

            self.print_ls.wrn(f"message_handler:{content}")

        await self.nc.publish(msg.reply, self.__ensure_encoded(content))

    async def subscribe_to_nats(self):
        self.print_ls.debug(f"initialize nats subscriptions")
        await self.nc.subscribe(f"agent.{config.cluster_id()}.request", cb=self.message_handler)
        await self.nc.subscribe(f"server.cmd", cb=self.__server_cmd_handler)

    async def __server_cmd_handler(self, msg):
        try:
            self.print_ls.debug(f"cmd from server")
            command = msg.data.decode()
            self.print_ls.debug(f"cmd from server. command : {command}")

            if command:
                command = json.loads(command)
                self.print_ls.debug(f"force registration and subscription")
                if command['command'] == 'restart':
                    self.print_ls.debug(f"run.registration")
                    await self.client_registration()
                    self.print_ls.debug(f"run.subscription")
                    await self.subscribe_to_nats()

        except Exception as e:
            self.print_ls.wrn(f"__server_cmd_handler ({str(e)})")

    async def __send_client_alive(self):
        subject = f"status.client.{self.channel_id}"
        data = {'client': self.nc.client_id, 'name': config.cluster_id(), 'status': 'alive'}

        # Convert the dictionary to a JSON string
        message = json.dumps(data)
        interval = self.alive_sec

        # initial sleep
        await asyncio.sleep(interval)
        while True:
            try:
                if self.nc.is_connected:
                    self.print_ls.trace(f"alive message {subject}: {message}")
                    response = await self.nc.request(subject, message.encode(),
                                                     timeout=self.timeout_request)
                    self.print_ls.trace(f"__send_client_alive .Received reply: {response.data.decode()}")
            except ErrTimeout:
                self.print_ls.wrn("__send_client_alive No reply received from server (timeout)")
            except ErrNoServers:
                self.print_ls.wrn("__send_client_alive No reply received (no nats server)")
            except Exception as e:
                self.print_ls.wrn(f"__send_client_alive ({str(e)})")
            finally:
                await asyncio.sleep(interval)  # Publish every x seconds

    async def __get_data_from_api(self, path, credential: bool = False):

        self.print_ls.debug(f"__get_data_from_api {path}")
        try:
            if credential:
                # create temp user
                user = User()
                user.username = "nats"
                user.is_nats = True
                user.cp_mapping_user = 'local-nats'
                current_user_var.set(user)
                cp_user.set("local-nats")

            endpoint_function = self.__get_endpoint_function_by_path(self.app, path)
            response = await endpoint_function()

            if isinstance(response, JSONResponse):
                return json.loads(response.body.decode())

            return response
        except Exception as e:
            self.print_ls.wrn(f"__get_data_from_api ({str(e)})")
            return None

    async def __publish_kv_pair(self, key, value):
        try:
            self.print_ls.debug(f"__publish_kv_pair.key {key}")
            js = self.nc.jetstream()
            kv = await js.key_value(self.kv_bucket_name)

            data = self.__ensure_encoded(value)

            # await kv.put(key, json.dumps(value).encode())
            await kv.put(key, data)
            self.print_ls.debug(f"__publish_kv_pair.published {key}")
            return True

        except ErrTimeout:
            self.print_ls.wrn("__publish_kv_pair No reply received from server (timeout)")
        except ErrNoServers:
            self.print_ls.wrn("__publish_kv_pair No reply received (no nats server)")
        except Exception as e:
            self.print_ls.wrn(f"__publish_kv_pair ({str(e)})")

        return False

    async def __publish_data_to_kv(self):
        self.print_ls.info(f"__publish_data_to_kv.client {self.kv_bucket_name}")

        interval = 1

        # self.print_ls.info(f"__publish_data_to_kv.k8s health updated every {self.kv_health_k8s_interval} sec")
        # self.print_ls.info(f"__publish_data_to_kv.statistics updated every {self.kv_stats_interval} sec")
        self.kv_job_cron.print_info()

        # last_stats = self.kv_stats_interval + 1
        # last_health_k8s = self.kv_health_k8s_interval + 1
        # initial sleep
        await asyncio.sleep(5)
        while True:
            try:
                # last_stats += 1
                # last_health_k8s += 1
                self.kv_job_cron.add_tick_to_interval(1)

                # if last_stats > self.kv_stats_interval:
                #     last_stats = 0
                #     data = await self.__get_data_from_api(path=self.kv_stats_path, credential=True)
                #     if data is not None:
                #         update = await self.__publish_kv_pair(key=self.kv_stats_name, value=data)
                #         self.print_ls.info(f"__publish_data_to_kv. update {self.kv_stats_name} res: {update}")
                #
                # if last_health_k8s > self.kv_health_k8s_interval:
                #     last_health_k8s = 0
                #     data = await self.__get_data_from_api(path=self.kv_health_path)
                #     if data is not None:
                #         update = await self.__publish_kv_pair(key=self.kv_health_k8s_name, value=data)
                #         self.print_ls.info(f"__publish_data_to_kv. update {self.kv_health_k8s_name} res: {update}")
                #     else:
                #         self.print_ls.wrn("__publish_data_to_kv. No data published")
                for name, job in self.kv_job_cron.jobs.items():
                    if job.is_elapsed:
                        self.print_ls.trace(f"__publish_data_to_kv. batch {name}")
                        job.reset_timer()
                        data = await self.__get_data_from_api(path=job.endpoint,
                                                              credential=job.credential)
                        if data and data is not None:
                            # print(f"---->{data}")

                            data['data']['metadata'] = {'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                                                        'jetstream': True}
                            # print(f"------>{data['data']['metadata']}")
                            update = await self.__publish_kv_pair(key=job.ky_key,
                                                                  value=data)

                            self.print_ls.info(f"__publish_data_to_kv. update {job.ky_key} res: {update}")

            except ErrTimeout:
                self.print_ls.wrn("__publish_data_to_kv No reply received from server (timeout)")
            except ErrNoServers:
                self.print_ls.wrn("__publish_data_to_kv No reply received (no nats server)")
            except Exception as e:
                self.print_ls.wrn(f"__publish_data_to_kv ({str(e)})")
            finally:
                await asyncio.sleep(interval)  # Publish every x seconds

    async def run(self):
        self.print_ls.debug(f"run")

        self.print_ls.debug(f"run.connection")
        await self.get_nats_connection()

        self.print_ls.debug(f"run.registration")
        await self.client_registration()
        self.print_ls.debug(f"run.create bucket  {self.kv_bucket_name}")
        await self.create_bucket_store(key_value=self.kv_bucket_name)

        self.print_ls.debug(f"run.subscription")
        await self.subscribe_to_nats()

        # Create a task to publish messages at intervals
        publish_status = asyncio.create_task(self.__send_client_alive())

        # Create a task to publish status to kv value at intervals
        publish_kv_status = asyncio.create_task(self.__publish_data_to_kv())

        # Keep the receiver running
        await asyncio.Event().wait()


natsManager = None


async def boot_nats_start_manager(app):
    global natsManager
    natsManager = NatsManager(app)
    try:
        await natsManager.run()
    except KeyboardInterrupt:
        print("Interrupted by user, shutting down.")


def get_nats_manager_instance():
    return natsManager

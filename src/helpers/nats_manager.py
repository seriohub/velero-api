import json
import nats

from fastapi import FastAPI
from fastapi.routing import APIRoute, Mount
from fastapi.testclient import TestClient

from core.config import ConfigHelper

from security.service.helpers.tokens import create_access_token

config = ConfigHelper()

class NatsManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(NatsManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, app):
        self.app = app
        self.nc = None

    async def __init_nats_connection(self):
        if self.nc is None:
            self.nc = await nats.connect("nats://localhost:4222")

    async def get_nats_connection(self):

        if self.nc is None:
            await self.__init_nats_connection()
        return self.nc

    @staticmethod
    def __get_endpoint_function_by_path(app_fastapi: FastAPI, path: str):
        # Helper function to search routes
        def search_routes(routes, path):
            for route in routes:
                # print("route", route)
                if isinstance(route, APIRoute) and route.path == path:
                    return route.endpoint
                elif isinstance(route, Mount):
                    # Check mounted sub-application routes
                    sub_app = route.app
                    sub_path = path[len(route.path.rstrip("/")):]
                    if sub_path:
                        sub_endpoint = search_routes(sub_app.routes, sub_path)
                        if sub_endpoint:
                            return sub_endpoint
            return None

        return search_routes(app_fastapi.routes, path)

    async def message_handler(self, msg):
        command = msg.data.decode()

        if command:
            command = json.loads(command)
        else:
            await self.nc.publish(msg.reply, "error".encode())

        print(f"Received a request via NATS method:{command['method']} \tpath:{command['path']} ")

        # path = "/api/info/get"
        endpoint_function = self.__get_endpoint_function_by_path(self.app, command['path'])
        if endpoint_function:
            access_token = create_access_token(
                data={'sub': 'nats', 'is_nats': True}
            )

            # Call endpoint function with TestClient
            if command['method'] == 'GET':
                response = TestClient(self.app).get(command['path'],
                                                    params=command['params'],
                                                    headers={"Authorization": f"Bearer {access_token}",
                                                             "cp_user": command["user"]})
            else:
                response = TestClient(self.app).post(command['path'],
                                                     json=command['params'],
                                                     headers={"Authorization": f"Bearer {access_token}",
                                                              "cp_user": command["user"]})
            content = response.content
        else:
            content = f"No endpoint found for path: {endpoint_function}"

        await self.nc.publish(msg.reply, content)

    async def subscribe_to_nats(self):
        print("initialize nats subscriptions")
        await self.nc.subscribe("agent.command.request.subject", cb=self.message_handler)

    async def run(self):
        await self.get_nats_connection()
        await self.subscribe_to_nats()


natsManager = None

async def boot_nats_start_manager(app):
    global natsManager
    natsManager = NatsManager(app)
    await natsManager.run()

def get_nats_manager_instance():
    return natsManager

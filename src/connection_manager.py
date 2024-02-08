from typing import List
from fastapi import WebSocket
from helpers.handle_exceptions import *


# socket manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    @handle_exceptions_instance_method
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    @handle_exceptions_instance_method
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    @handle_exceptions_instance_method
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    @handle_exceptions_instance_method
    async def broadcast(self, message: str):
        #
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as Ex:
                # print("error", Ex)
                pass


manager = ConnectionManager()

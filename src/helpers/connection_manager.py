from fastapi import WebSocket
from typing import Dict

from security.service.helpers.users import get_current_user_token

# socket manager
class ConnectionManager:
    def __init__(self):
        # self.active_connections: List[WebSocket] = []
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket):
        try:
            await websocket.accept()
            token = await websocket.receive_text()
            user = await get_current_user_token(token)
            print(f"Connected user via socket: {user.username}")
            if user is not None and not user.is_disabled:
                self.active_connections[str(user.id)] = websocket
                await self.send_personal_message(str(user.id), 'Connection READY!')
            else:
                await websocket.close(1001)
        except:
            await websocket.close(1001)

    def disconnect(self, user_id):
        self.active_connections[user_id].close(1001)
        del self.active_connections[user_id]

    async def send_personal_message(self, user_id, message: str):
        try:
            await self.active_connections[user_id].send_text(message)
        except:
            pass

    async def broadcast(self, message: str):
        for user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(message)
            except Exception as Ex:
                print("error", Ex)


manager = ConnectionManager()

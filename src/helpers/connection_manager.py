from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict
import json
import traceback
# import asyncio

from security.service.helpers.users import get_current_user_token


# socket manager
class ConnectionManager:
    def __init__(self):
        # self.active_connections: List[WebSocket] = []
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket):
        try:
            await websocket.accept()
            # while True:
            try:
                token = await websocket.receive_text()
            except Exception as e:
                print(f"WebSocket Receive Error: {e}")
                traceback.print_exc()
                # await self.disconnect_websocket(websocket)
                # break
                return

            user = await get_current_user_token(token)
            if user is not None and not user.is_disabled:
                self.active_connections[str(user.id)] = websocket
                response = {'response_type': 'notification', 'message': 'Connection READY!'}
                await self.send_personal_message(str(user.id), json.dumps(response))

                # Start keep-alive pings
                # asyncio.create_task(self.keep_alive(websocket))
                await self.listen_for_messages(websocket, str(user.id))
            else:
                await websocket.close(1001)
                # break
        except WebSocketDisconnect:
            await websocket.close(1001)
        except Exception as e:
            await websocket.close(1001)
            print(f"WebSocket connection error: {e}")

    # async def keep_alive(self, websocket: WebSocket):
    #     """ Periodically sends ping messages to prevent timeouts """
    #     try:
    #         while True:
    #             await asyncio.sleep(30)  # Adjust time as needed
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
                print(f"WebSocket for user {user_id} was already closed.")
            finally:
                self.active_connections.pop(user_id, None)
                print(f"Disconnected user {user_id} and removed from active connections.")

    def disconnect(self, user_id):
        self.active_connections[user_id].close(1001)
        del self.active_connections[user_id]

    async def send_personal_message(self, user_id, message: str):
        try:
            await self.active_connections[str(user_id)].send_text(message)
        except KeyError:
            print(f"User ID {user_id} not found in active connections.")
        except AttributeError:
            print(f"Connection object for user ID {user_id} does not support send_text method.")
        except Exception as e:
            print(f"An unexpected error occurred while sending message to user ID {user_id}: {str(e)}")

    async def broadcast(self, message: str):
        for user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(message)
            except Exception as Ex:
                print("error", Ex)

    async def listen_for_messages(self, websocket: WebSocket, user_id: str):
        """Listen for incoming messages from the client"""
        print(f"Start listen for incoming messages from the client.....")
        try:
            while True:
                message = await websocket.receive_text()
                print(f"Received message from user {user_id}: {message}")

                # Handle different types of messages
                try:
                    data = json.loads(message)
                    if "action" in data:
                        if data["action"] == "ping":
                            await websocket.send_text(json.dumps({"type": "pong"}))
                        elif data["action"] == "broadcast":
                            await self.broadcast(json.dumps({"message": data.get("message", "")}))
                        elif data["action"] == "private_message":
                            target_user = data.get("target_user")
                            msg = data.get("message", "")
                            if target_user:
                                await self.send_personal_message(target_user, msg)
                    else:
                        print("Invalid message format.")
                except json.JSONDecodeError:
                    print(f"Invalid JSON message from user {user_id}: {message}")

        except WebSocketDisconnect:
            print(f"User {user_id} disconnected.")
            await self.disconnect_websocket(websocket)

        except Exception as e:
            print(f"Error in listen_for_messages: {e}")
            await self.disconnect_websocket(websocket)


manager = ConnectionManager()

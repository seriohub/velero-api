from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict
import json
import traceback

# from security.authentication.tokens import get_user_from_token
from security.authentication.tokens import get_user_entity_from_token


# socket manager
class WebSocketManager:
    def __init__(self):
        # self.active_connections: List[WebSocket] = []
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket):
        """Manages the WebSocket connection and authenticates the user only after receiving a valid token."""
        try:
            await websocket.accept()
            user = None  # Initialize the user as None

            while user is None:  # Continue until it receives a valid token
                try:
                    message = await websocket.receive_text()
                    data = json.loads(message) if message.startswith('{') else message  # Try decoding JSON
                except Exception as e:
                    print(f"WebSocket Receive Error: {e}")
                    traceback.print_exc()
                    return  # Terminate the connection if there is an error in receiving the message

                if isinstance(data, dict) and "action" in data and data["action"] == "ping":
                    # Responds to ping to keep the connection open
                    await websocket.send_text(json.dumps({"type": "pong"}))
                    continue  # Continue to receive messages without closing the connection

                elif isinstance(data, str):
                    # Treats the message as a JWT token
                    # user = await get_user_from_token(data)
                    user = await get_user_entity_from_token(data)

                if user is not None:
                    self.active_connections[str(user.id)] = websocket
                    response = {'response_type': 'notification', 'message': 'Connection READY!'}
                    await self.send_personal_message(str(user.id), json.dumps(response))

                    # Start listening to messages for authenticated users only
                    await self.listen_for_messages(websocket, str(user.id))
                    return  # Ends the loop after authenticating the user

            # If no valid token has been received, close the connection
            await websocket.close(1001)

        except WebSocketDisconnect:
            print("WebSocket disconnected")
            await websocket.close(1001)
        except Exception as e:
            print(f"WebSocket connection error: {e}")
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


manager = WebSocketManager()

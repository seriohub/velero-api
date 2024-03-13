from pydantic import BaseModel
from typing import Any


class SuccessfulRequest(BaseModel):
    data: dict = {
        'payload': {},
        'metadata': {}
    }
    notifications: list = []
    messages: list = []

    def __init__(self, payload=None, metadata=None, notifications=None, messages=None, **data: Any):
        super().__init__(**data)
        if metadata is None:
            metadata = {}
        if payload is None:
            payload = {}
        if notifications is None:
            notifications = []
        if messages is None:
            messages = []
        self.data['payload'] = payload
        self.data['metadata'] = metadata
        self.notifications = notifications
        self.messages = messages

    def toJSON(self):
        return {'data': self.data,
                'notifications': self.notifications,
                'messages': self.messages
                }

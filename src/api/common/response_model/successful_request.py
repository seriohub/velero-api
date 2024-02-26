from pydantic import BaseModel
from typing import Any


class SuccessfulRequest(BaseModel):
    data: dict = {
        'payload': {},
        'metadata': {}
    }
    messages: list = []

    def __init__(self, payload=None, metadata=None, messages=None, **data: Any):
        super().__init__(**data)
        if metadata is None:
            metadata = {}
        if payload is None:
            payload = {}
        if messages is None:
            messages = []
        self.data['payload'] = payload
        self.data['metadata'] = metadata
        self.messages = messages

    def toJSON(self):
        return {'data': self.data,
                'messages': self.messages
                }

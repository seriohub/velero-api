from typing import Any

from pydantic import BaseModel, Field


class FailedRequest(BaseModel):
    error: dict = Field({
         'title': '',
         'description': ''
    })
    messages: list = []

    def __init__(self, title='', description='', messages=None, **data: Any):
        super().__init__(**data)
        if messages is None:
            messages = []
        self.error['title'] = title
        self.error['description'] = description
        self.messages = messages

    def toJSON(self):
        return {'error': self.error,
                'messages': self.messages
                }

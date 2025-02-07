from typing import Any

from pydantic import BaseModel, Field


class FailedRequest(BaseModel):
    error: dict = Field({
        'title': '',
        'description': ''
    })
    notifications: list = []
    messages: list = []

    def __init__(self, title='', description='', notifications=None, messages=None, **data: Any):
        super().__init__(**data)
        if notifications is None:
            notifications = []
        if messages is None:
            messages = []
        self.error['title'] = title
        self.error['description'] = description
        self.notifications = notifications
        self.messages = messages

    def toJSON(self):
        return {'error': self.error,
                'notifications': self.notifications,
                # 'alerts': self.alerts
                }

from pydantic import BaseModel, Field
from enum import Enum
import pickle

class MessageType(Enum):
    INFO = "Info"
    WARNING = "Warning"
    ERROR = "Error"


class Message:
    title: str
    description: str
    type: MessageType


class SuccessfulRequest(BaseModel):
    data: dict = {}
    messages: list = []

    def toJSON(self):
        return {'data': self.data,
                'messages': self.messages
                }


class FailedRequest(BaseModel):
    error: dict = Field({
         'title': '',
         'description': ''
    })
    messages: list = []

    def toJSON(self):
        return {'error': self.error,
                'messages': self.messages
                }


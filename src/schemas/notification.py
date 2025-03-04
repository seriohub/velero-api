from pydantic import BaseModel


class Notification(BaseModel):
    title: str = ''
    description: str = ''
    type: str = 'INFO'

    def __init__(self, title='', description='', type_='INFO'):
        super().__init__()
        self.title = title
        self.description = description
        self.type = type_

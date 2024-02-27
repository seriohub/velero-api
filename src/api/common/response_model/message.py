class Message:
    def __init__(self, title='', description='', type='INFO'):
        self.title = title
        self.description = description
        self.type = type

    def toJSON(self):
        return {'title': self.title,
                'description': self.description,
                'type': self.type,
                }

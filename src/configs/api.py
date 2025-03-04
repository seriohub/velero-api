import os


class APIConfig:
    def __init__(self):
        self.endpoint_url = os.getenv('API_ENDPOINT_URL', '127.0.0.1')
        self.endpoint_port = int(os.getenv('API_ENDPOINT_PORT', '8090'))

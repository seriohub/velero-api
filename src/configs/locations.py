import os


class LocationConfig:
    def __init__(self):
        self.aws_ssl = os.getenv('AWS_SECURE_CONNECTION', 'False').lower() == 'true'

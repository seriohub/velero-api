import os


class ApplicationConfig:
    def __init__(self):
        self.build_version = os.getenv('BUILD_VERSION', 'dev')
        self.build_date = os.getenv('BUILD_DATE', '-')
        self.admin_email = os.getenv('ADMIN_EMAIL', 'not set')
        self.uvicorn_reload = os.getenv('UVICORN_RELOAD', 'False').lower() == 'true'
        self.auth_enabled = os.getenv('AUTH_ENABLED', 'True').lower() == 'true'
        self.auth_type = os.getenv('AUTH_TYPE', 'BUILT-IN')
        self.swagger_documentation_disabled = os.getenv('API_ENABLE_DOCUMENTATION', '0') == '1'
        # self.container_mode = os.getenv('CONTAINER_MODE', 'False').lower() == 'true'
        self.scrapy_version = int(os.getenv('SCRAPY_VERSION_MIN', '30'))

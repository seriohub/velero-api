import os

class DatabaseConfig:
    def __init__(self):
        self.database_path = self._sanitize_path(os.getenv('SECURITY_PATH_DATABASE', './'))
        self.default_admin_user = os.getenv('DEFAULT_ADMIN_USERNAME', 'admin')
        self.default_admin_password = os.getenv('DEFAULT_ADMIN_PASSWORD', 'admin')

    @staticmethod
    def _sanitize_path(path):
        """Removes any initial and final slashes to normalize the pathway"""
        if not path or path == '/':
            return './'  # Default fallback

        return path.strip('/') if len(path) > 1 else './'

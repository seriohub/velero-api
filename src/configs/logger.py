import os

class LoggerConfig:
    VALID_LOG_LEVELS = {'critical', 'error', 'warning', 'info', 'debug', 'trace', 'notset'}

    def __init__(self):
        # self.log_key = os.getenv('LOG_KEY', 'k8s-wdt')
        # self.log_format = os.getenv('LOG_FORMAT', '%(asctime)s :: [%(levelname)s] :: %(message)s')
        # self.save_to_file = os.getenv('LOG_SAVE', 'False').lower() == 'true'
        # self.folder = os.getenv('LOG_DEST_FOLDER', './logs')
        # self.filename = os.getenv('LOG_FILENAME', 'k8s.log')
        # self.max_filesize = int(os.getenv('LOG_MAX_FILE_SIZE', 4000000))
        # self.backups = int(os.getenv('LOG_FILES_BACKUP', 5))
        self.debug_level = self._validate_log_level(os.getenv('DEBUG_LEVEL', 'info'))

    def _validate_log_level(self, level):
        return level.lower() if level and level.lower() in self.VALID_LOG_LEVELS else "info"

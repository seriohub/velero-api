import logging

WATCH_LEVEL = 25
logging.addLevelName(WATCH_LEVEL, "WATCH")

LEVEL_MAPPING = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'watch': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}

# Color ANSI code
COLORS = {
    'DEBUG': '\033[94m',  # Blue
    'INFO': '\033[92m',  # Green
    'WATCH': '\033[96m',  # Cyan
    'WARNING': '\033[93m',  # Yellow
    'ERROR': '\033[91m',  # Red
    'CRITICAL': '\033[95m',  # Purple
}

RESET = '\033[0m'

# Icons for levels
LEVEL_ICONS = {
    'DEBUG': '🐞',
    'INFO': 'ℹ️',
    'WATCH': '👀',
    'WARNING': '⚠️',
    'ERROR': '❌',
    'CRITICAL': '🔥'
}

# class ColoredFormatter(logging.Formatter):
#     """
#     Custom formatter that adds color to messages based on level.
#     """
#
#     def format(self, record):
#         # Retrieve the level and apply the corresponding color
#         level_name = record.levelname
#         if level_name in COLORS:
#             colored_levelname = f"{COLORS[level_name]}{level_name}{RESET}"
#             record.levelname = colored_levelname
#             record.msg = f"{COLORS[level_name]}{record.msg}{RESET}"
#         return super().format(record)


class ColoredFormatter(logging.Formatter):
    """
    Custom formatter that adds color and icons to messages based on level.
    """

    def format(self, record):
        # Retrieve the level and apply the corresponding color and icon
        levelname = record.levelname
        icon = LEVEL_ICONS.get(levelname, '')

        if levelname in COLORS:
            colored_levelname = f"{COLORS[levelname]}{icon} APP {levelname}{RESET}"
            record.levelname = colored_levelname
            record.msg = f"{COLORS[levelname]}{record.msg}{RESET}"

        return super().format(record)

class ColoredLogger:
    """
    Class to get a configured logger with colored output.
    """

    @staticmethod
    def get_logger(name: str, level: int = logging.DEBUG) -> logging.Logger:
        """
        Returns a logger with the colored formatter.

        :param name: Name of the logger.
        :param level: Level of logging (default: logging.DEBUG).
        :return: configured logger.
        """
        logger = logging.getLogger(name)
        logger.setLevel(level)

        # Check if the logger already has handlers to avoid duplicates
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = ColoredFormatter(
                '%(asctime)s %(levelname)s - %(filename)s[%(lineno)d]->%(funcName)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        def watch(self, message, *args, **kwargs):
            if self.isEnabledFor(WATCH_LEVEL):
                self._log(WATCH_LEVEL, message, args, **kwargs)

        setattr(logger, 'watch', watch.__get__(logger))

        return logger

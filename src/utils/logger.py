import logging

LEVEL_MAPPING = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}

# Codici ANSI per i colori
COLORS = {
    'DEBUG': '\033[94m',  # Blue
    'INFO': '\033[92m',  # Green
    'WARNING': '\033[93m',  # Yellow
    'ERROR': '\033[91m',  # Red
    'CRITICAL': '\033[95m',  # Purple
}
RESET = '\033[0m'


class ColoredFormatter(logging.Formatter):
    """
    Custom formatter that adds color to messages based on level.
    """

    def format(self, record):
        # Retrieve the level and apply the corresponding color
        levelname = record.levelname
        if levelname in COLORS:
            colored_levelname = f"{COLORS[levelname]}{levelname}{RESET}"
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
                '%(asctime)s - %(filename)s[%(lineno)d]->%(funcName)s - %(levelname)s %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

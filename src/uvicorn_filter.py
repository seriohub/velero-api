import logging
import sys
from logging.config import dictConfig

# ANSI Colors
COLORS = {
    'DEBUG': '\033[94m',  # Blue
    'INFO': '\033[92m',  # Green
    'WARNING': '\033[93m',  # Yellow
    'ERROR': '\033[91m',  # Red
    'CRITICAL': '\033[95m',  # Purple
}
RESET = '\033[0m'

# Icons for levels
LEVEL_ICONS = {
    'DEBUG': '🐞',
    'INFO': 'ℹ️',
    'WARNING': '⚠️',
    'ERROR': '❌',
    'CRITICAL': '🔥'
}


class CustomFormatter(logging.Formatter):
    """
    Custom formatter that adds color and icons to messages based on level.
    """

    def format(self, record):
        levelname = record.levelname
        icon = LEVEL_ICONS.get(levelname, '')

        if levelname in COLORS:
            colored_levelname = f"{COLORS[levelname]}{icon} UVC {levelname}{RESET}"
            record.levelname = colored_levelname
            record.msg = f"{COLORS[levelname]}{record.msg}{RESET}"

        return super().format(record)


# Configurazione manuale del logging
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "colored": {
            "()": CustomFormatter,
            "fmt": "%(asctime)s %(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "colored",
            "stream": sys.stdout
        }
    },
    "loggers": {
        "uvicorn": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False
        },
        "uvicorn.access": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False
        },
        "uvicorn.error": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False
        },
        "app": {
            "level": "DEBUG",
            "handlers": ["console"],
            "propagate": False
        }
    }
}

# Applica la configurazione
dictConfig(LOGGING_CONFIG)

# Crea e assegna i logger
uvicorn_logger = logging.getLogger("uvicorn")
uvicorn_access_logger = logging.getLogger("uvicorn.access")
uvicorn_error_logger = logging.getLogger("uvicorn.error")
app_logger = logging.getLogger("app")

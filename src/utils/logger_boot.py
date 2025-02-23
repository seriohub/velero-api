from configs.config_boot import config_app
from utils.logger import ColoredLogger, LEVEL_MAPPING
import logging

logger = ColoredLogger.get_logger(__name__, level=LEVEL_MAPPING.get(config_app.get_internal_log_level(), logging.INFO))

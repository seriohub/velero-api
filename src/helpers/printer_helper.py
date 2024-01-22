import os
import logging
import sys
from logging.handlers import RotatingFileHandler
from helpers.handle_exceptions import handle_exceptions_instance_method
from libs.config import ConfigEnv


class LLogger:
    def __init__(self):
        self.logger = None

    @handle_exceptions_instance_method
    def init_logger_from_config(self, cl_config: ConfigEnv):
        # logger section
        logger_key = cl_config.logger_key()
        logger_format_msg = cl_config.logger_msg_format()
        logger_save_to_file = cl_config.logger_save_to_file()
        logger_folder = cl_config.logger_folder()
        logger_file_name = cl_config.logger_filename()
        logger_file_size = cl_config.logger_max_filesize()
        logger_backup_files = cl_config.logger_his_backups_files()
        logger_level = cl_config.logger_level()

        return self.init_logger(key=logger_key,
                                output_format=logger_format_msg,
                                save_to_file=logger_save_to_file,
                                destination_folder=logger_folder,
                                filename=logger_file_name,
                                max_file_size=logger_file_size,
                                historical_files=logger_backup_files,
                                level=logger_level)

    @handle_exceptions_instance_method
    def init_logger(self,
                    key,
                    output_format,
                    save_to_file,
                    destination_folder,
                    filename,
                    max_file_size,
                    historical_files,
                    level):
        if self.logger is None:

            logging.basicConfig(format=output_format,
                                level=level)
            self.logger = logging.getLogger(key)
            if save_to_file:
                print('INFO    logger folder files {0}'.format(filename))
                file_to_log = os.path.join(destination_folder, filename)
                handler = RotatingFileHandler(file_to_log,
                                              maxBytes=max_file_size,
                                              backupCount=historical_files)
                formatter = logging.Formatter(output_format)
                handler.setFormatter(formatter)
                self.logger.addHandler(handler)

            # self.logger.setLevel(logging.DEBUG)

        return self.logger


class BColors:
    """
    Define colors for formatting log string
    """
    HEADER = '\033[95m'
    OK_BLUE = '\033[94m'
    OK_CYAN = '\033[96m'
    OK_GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    END_C = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class PrintHelper:
    def __init__(self, namespace, logger=None):
        self.msg_len = 10
        self.logger_enable = False
        self.logger = None
        self.set_logger(logger)
        self.name = namespace
        self.colored_stdout = True

    @handle_exceptions_instance_method
    def __composer_str__(self,
                         color=None,
                         title='',
                         message='',
                         stdout: bool = False):
        ret = f"{self.name} {message}"
        if title:
            ret = f"{title.ljust(self.msg_len, ' ')}{ret}"

        if self.colored_stdout and color is not None:
            ret = f"{color}{ret}{BColors.END_C}"
        if stdout:
            print(ret)
        return ret

    @handle_exceptions_instance_method
    def set_logger(self, logger):
        self.logger = logger
        if self.logger is not None:
            self.logger_enable = True

    @handle_exceptions_instance_method
    def debug_if(self, enable=True, msg=''):
        if enable:
            if self.logger_enable:
                message = self.__composer_str__(color=BColors.OK_CYAN,
                                                message=msg)
                self.logger.debug(message)
            else:
                self.debug(msg)

    @handle_exceptions_instance_method
    def debug(self, msg):
        if self.logger_enable:
            message = self.__composer_str__(color=BColors.OK_CYAN,
                                            message=msg)
            self.logger.debug(message)
        else:
            title = 'DEBUG:'
            self.__composer_str__(color=BColors.OK_CYAN,
                                  title=title,
                                  message=msg,
                                  stdout=True)

    @handle_exceptions_instance_method
    def highlights(self, msg):
        if self.logger_enable:
            message = self.__composer_str__(color=BColors.OK_GREEN,
                                            message=msg)
            self.logger.info(message)
        else:
            title = 'INFO:'
            self.__composer_str__(color=BColors.OK_GREEN,
                                  title=title,
                                  message=msg,
                                  stdout=True)

    @handle_exceptions_instance_method
    def info_if(self, enable=True, msg=''):
        if enable:
            if self.logger_enable:
                message = self.__composer_str__(color=None,
                                                message=msg)
                self.logger.info(message)
            else:
                self.info(msg)

    @handle_exceptions_instance_method
    def info(self, msg):
        if self.logger_enable:
            message = self.__composer_str__(color=None,
                                            message=msg)
            self.logger.info(message)
        else:
            title = 'INFO:'
            self.__composer_str__(color=None,
                                  title=title,
                                  message=msg,
                                  stdout=True)

    @handle_exceptions_instance_method
    def wrn(self, msg):
        if self.logger_enable:
            message = self.__composer_str__(color=BColors.WARNING,
                                            message=msg)
            self.logger.warning(message)
        else:
            title = 'WARNING:'
            self.__composer_str__(color=BColors.WARNING,
                                  title=title,
                                  message=msg,
                                  stdout=True)

    @handle_exceptions_instance_method
    def alert(self, msg):
        if self.logger_enable:
            message = self.__composer_str__(color=BColors.BOLD,
                                            message=msg)
            self.logger.fatal(message)
        else:
            title = 'ALERT:'
            self.__composer_str__(color=BColors.BOLD,
                                  title=title,
                                  message=msg,
                                  stdout=True)

    @handle_exceptions_instance_method
    def error(self, msg):
        if self.logger_enable:
            message = self.__composer_str__(color=BColors.FAIL,
                                            message=msg)
            self.logger.error(message)
        else:
            title = 'ERROR:'
            self.__composer_str__(color=BColors.FAIL,
                                  title=title,
                                  message=msg,
                                  stdout=True)

    @handle_exceptions_instance_method
    def error_and_exception(self,
                            procedure_name,
                            error):
        exc_type, exc_obj, exc_tb = sys.exc_info()
        msg = f"line: {exc_tb.tb_lineno} {str(error)} type:{exc_type}"
        if self.logger_enable:
            message = self.__composer_str__(color=BColors.FAIL,
                                            message=f"{procedure_name} {msg}")
            self.logger.error(message)
        else:
            title = 'ERROR:'
            self.__composer_str__(color=BColors.FAIL,
                                  title=title,
                                  message=msg,
                                  stdout=True)

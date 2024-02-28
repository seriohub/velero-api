import sys


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


class PrintLevel:
    NOTSET = 0
    TRACE = 5
    DEBUG = 10
    INFO = 20
    WARN = 30
    ERROR = 40
    CRITICAL = 50


class PrintHelper:

    def __init__(self, namespace, logger=None, level=None):
        self.msg_len = 10
        self.logger_enable = False
        self.logger = None
        self.set_logger(logger)
        self.name = namespace
        self.colored_stdout = True
        self.print_level = PrintLevel.NOTSET
        if level is not None:
            self.set_print_level(level)

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

    def set_print_level(self, level=None):
        # level[critical | error | warning | info | debug | trace]
        self.print_level = PrintLevel.NOTSET

        if level is not None:
            match level.lower():
                case "critical":
                    self.print_level = PrintLevel.CRITICAL
                case "error":
                    self.print_level = PrintLevel.ERROR
                case "warning":
                    self.print_level = PrintLevel.WARN
                case "info":
                    self.print_level = PrintLevel.INFO
                case "debug":
                    self.print_level = PrintLevel.DEBUG
                case "trace":
                    self.print_level = PrintLevel.TRACE
                case _:
                    self.print_level = PrintLevel.NOTSET

    def set_logger(self, logger):
        self.logger = logger
        if self.logger is not None:
            self.logger_enable = True

    # def debug_if(self, enable=True, msg=''):
    #     if enable or self.print_level <= PrintLevel.DEBUG:
    #         if self.logger_enable:
    #             message = self.__composer_str__(color=BColors.OK_CYAN,
    #                                             message=msg)
    #             self.logger.debug(message)
    #         else:
    #             self.debug(msg)

    def debug(self, msg):
        if self.print_level <= PrintLevel.DEBUG:
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

    # LS 2024.02.27 add trace function
    def trace(self, msg):
        if self.print_level <= PrintLevel.TRACE:
            if self.logger_enable:
                message = self.__composer_str__(color=BColors.OK_CYAN,
                                                message=msg)
                self.logger.debug(message)
            else:
                title = 'TRACE:'
                self.__composer_str__(color=BColors.OK_CYAN,
                                      title=title,
                                      message=msg,
                                      stdout=True)

    def highlights(self, msg):
        if self.print_level <= PrintLevel.INFO:
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

    # def info_if(self, enable=True, msg=''):
    #     if enable:
    #         if self.logger_enable:
    #             message = self.__composer_str__(color=None,
    #                                             message=msg)
    #             self.logger.info(message)
    #         else:
    #             self.info(msg)

    def info(self, msg):
        if self.print_level <= PrintLevel.INFO:
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

    def wrn(self, msg):
        if self.print_level <= PrintLevel.WARN:
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

    def alert(self, msg):
        if self.print_level <= PrintLevel.CRITICAL:
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

    def error(self, msg):
        if self.print_level <= PrintLevel.ERROR:
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

    def error_and_exception(self,
                            procedure_name,
                            error):
        if self.print_level <= PrintLevel.ERROR:
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

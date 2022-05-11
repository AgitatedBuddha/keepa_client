import logging
import inspect
from colorlog import ColoredFormatter

class Log:
    __log = {}

    def __init__(self, logger):
        if logger not in Log.__log:
            self.loggy = logging.getLogger(logger)
            self.loggy.setLevel(logging.DEBUG)
            self.ch = logging.StreamHandler()
            formatter = ColoredFormatter(
            "%(asctime)s - %(log_color)s%(levelname)s - %(white)s%(name)s:%(green)s%(message)s",
            datefmt=None,
            reset=True,
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red',
            }
            )
            self.ch.setFormatter(formatter)
            self.loggy.addHandler(self.ch)
            Log.__log.setdefault(logger, self.loggy)
        else:
            self.loggy = Log.__log.get(logger)

    def info(self, msg):
        frame = inspect.currentframe()
        self.loggy.info('{0} - {1}'.format(frame.f_back.f_lineno, msg))

    def debug(self, msg):
        frame = inspect.currentframe()
        self.loggy.debug('{0} - {1}'.format(frame.f_back.f_lineno, msg))

    def error(self, msg):
        frame = inspect.currentframe()
        self.loggy.error('{0} - {1}'.format(frame.f_back.f_lineno, msg))

    def warning(self, msg):
        frame = inspect.currentframe()
        self.loggy.warning('{0} - {1}'.format(frame.f_back.f_lineno, msg))
import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import logging as logging
import logging.config as config
import datetime

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.

# Constants
DEBUG_LARGEDATA = { 'val':5, 'desc':'DUMP' }
DEBUG = { 'val':10, 'desc':'DEBUG' }
INFO = { 'val':20, 'desc':'INFO' }
WARNING = { 'val':30, 'desc':'WARNING' }
ERROR = { 'val':40, 'desc':'ERROR' }
CRITICAL = { 'val':50, 'desc':'CRITICAL' }

LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "[S] %(asctime)s [%(levelname)] %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "standard",
                "stream": "ext://sys.stdout"
            }
        },
        "loggers": {
            "": {
                "level": "DEBUG",
                "handlers": ["console"]
            }
        }
    }

class ServerLogger():
    def __init__(self, config, level):
        logging.config.dictConfig(config)
        self.logger = logging.getLogger(__name__)
        self.level = level

    def log(self, msg=None, *args, **kwargs):
        current = datetime.datetime.now()
        output = f" [{self.level.get('desc')}] {msg} " if self.level.get('val') < DEBUG.get('val') else f" {msg} "
        if len(args) > 0: output = "{a} {b}".format(a=output, b=args)
        if len(kwargs) > 0: output = "{a} {b}".format(a=output, b=kwargs)
        if self.level == DEBUG_LARGEDATA or self.level == DEBUG:
            self.logger.debug(output)
        elif self.level == INFO:
            self.logger.info(output)
        elif self.level == WARNING:
            self.logger.warning(output)
        elif self.level == ERROR:
            self.logger.error(output)
        elif self.level == CRITICAL:
            self.logger.critical(output)

dump = ServerLogger(config=LOGGING_CONFIG, level=DEBUG_LARGEDATA)
debug = ServerLogger(config=LOGGING_CONFIG, level=DEBUG)
info = ServerLogger(config=LOGGING_CONFIG, level=INFO)
warning = ServerLogger(config=LOGGING_CONFIG, level=WARNING)
error = ServerLogger(config=LOGGING_CONFIG, level=ERROR)
critical = ServerLogger(config=LOGGING_CONFIG, level=CRITICAL)

# @anvil.server.callable
# def log(name, message, level='DEBUG'):
#     config.dictConfig(LOGGING_CONFIG)
#     log = logging.getLogger(name)
#     if level == 'DEBUG':
#         log.debug(message)
#     elif level == 'INFO':
#         log.info(message)
#     elif level == 'WARNING':
#         log.warning(message)
#     elif level == 'ERROR':
#         log.error(message)
#     elif level == 'CRITICAL':
#         log.critical(message)

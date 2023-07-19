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
                "format": "[S] %(asctime)s [%(levelname)-8s] %(message)s"
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
    def __init__(self, func, level):
        self.level = level
        self.f = func

    def log(self, msg=None, *args, **kwargs):
        current = datetime.datetime.now()
        output = f" [{self.level.get('desc')}] {msg} " if self.level.get('val') < DEBUG.get('val') else f" {msg} "
        if len(args) > 0: output = "{a} {b}".format(a=output, b=args)
        if len(kwargs) > 0: output = "{a} {b}".format(a=output, b=kwargs)
        self.f(output)

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

dump = ServerLogger(func=logger.debug, level=DEBUG_LARGEDATA)
debug = ServerLogger(func=logger.debug, level=DEBUG)
info = ServerLogger(func=logger.info, level=INFO)
warning = ServerLogger(func=logger.warning, level=WARNING)
error = ServerLogger(func=logger.error, level=ERROR)
critical = ServerLogger(func=logger.critical, level=CRITICAL)

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

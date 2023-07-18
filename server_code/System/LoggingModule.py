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
LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": " %(asctime)s %(levelname)-8s %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "standard",
                "stream": "ext://sys.stdout"
            }
        },
        "loggers": {
            "": {
                "level": "INFO",
                "handlers": ["console"]
            }
        }
    }

class ServerLogger():
    def __init__(self, func, config, level):
        self.datefmt = config.datefmt
        self.default = config.default
        self.level = level
        self.f = func

    def log(self, msg=None, *args, **kwargs):
        log = logging.getLogger(name)
        if self.level.get('val') >= self.default.get('val'):
            current = datetime.datetime.now()
            output = f" {current.strftime(self.datefmt)} [{self.level.get('desc')}] {msg} "
            if len(args) > 0: output = "{a} {b}".format(a=output, b=args)
            if len(kwargs) > 0: output = "{a} {b}".format(a=output, b=kwargs)
            self.f(output)

dump = ServerLogger(func=log.debug, config=LOGGING_CONFIG, level=DEBUG_LARGEDATA)
debug = ServerLogger(func=log.debug, config=LOGGING_CONFIG, level=DEBUG)
info = ServerLogger(func=log.info, config=LOGGING_CONFIG, level=INFO)
warning = ServerLogger(func=log.warning, config=LOGGING_CONFIG, level=WARNING)
error = ServerLogger(func=log.error, config=LOGGING_CONFIG, level=ERROR)
critical = ServerLogger(func=log.critical, config=LOGGING_CONFIG, level=CRITICAL)

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

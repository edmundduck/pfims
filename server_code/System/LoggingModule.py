import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import logging as logging
import logging.config as config
import datetime
import psycopg2
import psycopg2.extras
from ..Utils.Caching import loglevel

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.

class ServerLoggerLevel:
    DEFAULT_LVL = logging.WARNING
    TRACE = {'val':logging.DEBUG-5, 'desc':'TRACE'}

class ServerLoggerConfig:
    DEFAULT_LOGGING_CONFIG = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'standard': {
                    'format': '[S] %(asctime)s [%(levelname)s] %(message)s'
                }
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'formatter': 'standard',
                    'stream': 'ext://sys.stdout'
                }
            },
            'loggers': {
                '': {
                    'level': 'DEBUG',
                    'handlers': ['console']
                }
            }
        }

class ServerLogger:

    # Cannot put function loglevel in level argument otherwise will cause nested loop (reason unknown)
    @staticmethod
    def init_logger(config=ServerLoggerConfig.DEFAULT_LOGGING_CONFIG, level=ServerLoggerLevel.DEFAULT_LVL):
        logger = logging.getLogger(__name__)
        logging.addLevelName(ServerLoggerLevel.TRACE.get('val'), ServerLoggerLevel.TRACE.get('desc'))
        logging.config.dictConfig(config)
        print("before call")
        anvil.server.session['loglevel'] = 5
        userlevel = anvil.server.session.get('loglevel')
        # userlevel=loglevel()
        print("after call")
        ServerLogger.logger.setLevel(userlevel if userlevel is not None else level)
        return logger

    @staticmethod
    def trace(msg=None, *args, **kwargs):
        ServerLogger.logger._log(ServerLoggerLevel.TRACE.get('val'), msg, args, **kwargs)

    @staticmethod
    def debug(msg=None, *args, **kwargs):
        print("debug,",ServerLogger.logger.level)
        print("anvil.server.session.get('loglevel'),",anvil.server.session.get('loglevel'))
        ServerLogger.logger.debug(msg, args, **kwargs)

    @staticmethod
    def info(msg=None, *args, **kwargs):
        ServerLogger.logger.info(msg, args, **kwargs)

    @staticmethod
    def warning(msg=None, *args, **kwargs):
        ServerLogger.logger.warning(msg, args, **kwargs)

    @staticmethod
    def error(msg=None, *args, **kwargs):
        ServerLogger.logger.error(msg, args, **kwargs)

    @staticmethod
    def critical(msg=None, *args, **kwargs):
        ServerLogger.logger.critical(msg, args, **kwargs)

def log_function(func):
    def wrapper(*args, **kwargs):
        # Log the function call
        ServerLogger.logger.debug("Server function %s starts ..." % func.__qualname__)
        # Call the original function
        result = func(*args, **kwargs)
        # Log the function return value
        ServerLogger.logger.debug("Server function %s returned: %s ///" % (func.__qualname__, result))
        return result
    return wrapper

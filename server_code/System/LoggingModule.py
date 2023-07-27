import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import logging as logging
import logging.config as config
import datetime
from .SystemModule import get_user_logging_level

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
    logger = None
    
    def __init__(self, config=ServerLoggerConfig.DEFAULT_LOGGING_CONFIG, level=get_user_logging_level()):
        logging.addLevelName(ServerLoggerLevel.TRACE.get('val'), ServerLoggerLevel.TRACE.get('desc'))
        logging.config.dictConfig(config)
        logger = logging.getLogger(__name__)
        logger.setLevel(level if level is not None else ServerLoggerLevel.DEFAULT_LVL)
        
    def trace(self, msg=None, *args, **kwargs):
        logger._log(ServerLoggerLevel.TRACE.get('val'), msg, args, **kwargs)

    def debug(self, msg=None, *args, **kwargs):
        logger.debug(msg, args, **kwargs)

    def info(self, msg=None, *args, **kwargs):
        logger.info(msg, args, **kwargs)

    def warning(self, msg=None, *args, **kwargs):
        logger.warning(msg, args, **kwargs)

    def error(self, msg=None, *args, **kwargs):
       logger.error(msg, args, **kwargs)

    def critical(self, msg=None, *args, **kwargs):
        logger.critical(msg, args, **kwargs)

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

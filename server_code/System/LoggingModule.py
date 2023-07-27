import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import logging as logging
import logging.config as config
import datetime
from .SystemModule import db_connect, get_current_userid, schemafin

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.

# Retrieve user logging level from DB table "settings", then save into session
# This function should not be placed in module importing Logger/Logging, otherwise circular import error will occur
@anvil.server.callable
def set_user_logging_level():
    conn = db_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(f"SELECT logging_level FROM {schemafin()}.settings WHERE userid='{get_current_userid()}'")
        result = cur.fetchone()
        anvil.server.session['logging_level'] = result.get('logging_level', None)
        print(f"({anvil.server.get_session_id()} set_user_logging_level={anvil.server.session}")

# Get user logging level from session
@anvil.server.callable
def get_user_logging_level():
    try:
        print(f"({anvil.server.get_session_id()} get_user_logging_level={anvil.server.session}")
        return anvil.server.session.get('logging_level')
    except AttributeError as err:
        return None

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
    logger = logging.getLogger(__name__)
    
    def __init__(self, config=ServerLoggerConfig.DEFAULT_LOGGING_CONFIG, level=get_user_logging_level()):
        logging.addLevelName(ServerLoggerLevel.TRACE.get('val'), ServerLoggerLevel.TRACE.get('desc'))
        logging.config.dictConfig(config)
        ServerLogger.logger.setLevel(level if level is not None else ServerLoggerLevel.DEFAULT_LVL)
        
    def trace(self, msg=None, *args, **kwargs):
        ServerLogger.logger._log(ServerLoggerLevel.TRACE.get('val'), msg, args, **kwargs)

    def debug(self, msg=None, *args, **kwargs):
        ServerLogger.logger.debug(msg, args, **kwargs)

    def info(self, msg=None, *args, **kwargs):
        ServerLogger.logger.info(msg, args, **kwargs)

    def warning(self, msg=None, *args, **kwargs):
        ServerLogger.logger.warning(msg, args, **kwargs)

    def error(self, msg=None, *args, **kwargs):
        ServerLogger.logger.error(msg, args, **kwargs)

    def critical(self, msg=None, *args, **kwargs):
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

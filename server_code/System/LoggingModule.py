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
TRACE = {'val':logging.DEBUG-5, 'desc':'TRACE'}

# Config - Customize the log level required here
def get_log_level():
    from . import SystemModule as sysmod
    log_level = sysmod.get_user_logging_level()
    return logging.WARNING if log_level is None else log_level

LOG_LEVEL = get_log_level()
LOGGING_CONFIG = {
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
                'level': 'TRACE',
                'handlers': ['console']
            }
        }
    }

class ServerLogger():
    def __init__(self, config, level):
        if isinstance(level, dict): logging.addLevelName(level.get('val'), level.get('desc'))
        logging.config.dictConfig(config)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(LOG_LEVEL)
        if isinstance(level, dict):
            self.f = self.trace
        elif level == logging.DEBUG:
            self.f = self.logger.debug
        elif level == logging.INFO:
            self.f = self.logger.info
        elif level == logging.WARNING:
            self.f = self.logger.warning
        elif level == logging.ERROR:
            self.f = self.logger.error
        elif level == logging.CRITICAL:
            self.f = self.logger.critical
        else:
            self.f = self.logger.warning

    def log_function(self, func):
        def wrapper(*args, **kwargs):
            # Log the function call
            self.f("Server function %s starts ..." % func.__qualname__)
            # Call the original function
            result = func(*args, **kwargs)
            # Log the function return value
            self.f("Server function %s returned: %s ///" % (func.__qualname__, result))
            return result
        return wrapper

    def log(self, msg=None, *args, **kwargs):
        current = datetime.datetime.now()
        if len(args) > 0: msg = '{a} {b}'.format(a=msg, b=args)
        if len(kwargs) > 0: msg = '{a} {b}'.format(a=msg, b=kwargs)
        self.f(msg)

    def trace(self, msg=None, *args, **kwargs):
        self.logger._log(TRACE.get('val'), msg, args, **kwargs)

trace = ServerLogger(config=LOGGING_CONFIG, level=TRACE)
debug = ServerLogger(config=LOGGING_CONFIG, level=logging.DEBUG)
info = ServerLogger(config=LOGGING_CONFIG, level=logging.INFO)
warning = ServerLogger(config=LOGGING_CONFIG, level=logging.WARNING)
error = ServerLogger(config=LOGGING_CONFIG, level=logging.ERROR)
critical = ServerLogger(config=LOGGING_CONFIG, level=logging.CRITICAL)
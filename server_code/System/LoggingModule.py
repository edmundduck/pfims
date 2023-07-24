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
        self.logger = logging.getLogger(__name__)
        if isinstance(level, dict): logging.addLevelName(level.get('val'), level.get('desc'))
        logging.config.dictConfig(config)
        # logging.root.setLevel(logging.DEBUG)
        self.level = level
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
        level = self.level.get('val') if isinstance(self.level, dict) else self.level
        output = f" [{self.level.get('desc')}] {msg} " if isinstance(self.level, dict) else f" {msg} "
        if len(args) > 0: output = '{a} {b}'.format(a=output, b=args)
        if len(kwargs) > 0: output = '{a} {b}'.format(a=output, b=kwargs)
        self.f(output)

    def trace(self, msg=None, *args, **kwargs):
        self.logger._log(TRACE.get('val'), msg, *args, **kwargs)

trace = ServerLogger(config=LOGGING_CONFIG, level=TRACE)
debug = ServerLogger(config=LOGGING_CONFIG, level=logging.DEBUG)
info = ServerLogger(config=LOGGING_CONFIG, level=logging.INFO)
warning = ServerLogger(config=LOGGING_CONFIG, level=logging.WARNING)
error = ServerLogger(config=LOGGING_CONFIG, level=logging.ERROR)
critical = ServerLogger(config=LOGGING_CONFIG, level=logging.CRITICAL)
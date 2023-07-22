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
DEBUG_LARGEDATA = {'val':logging.DEBUG-5, 'desc':'DUMP'}

LOGGING_CONFIG = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '[S] %(asctime)s [%(levelname)] %(message)s'
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

class ServerLogger():
    def __init__(self, config, level):
        self.logger = logging.getLogger(__name__)
        logging.config.dictConfig(config)
        logging.root.setLevel(logging.DEBUG)
        self.level = level

    def log(self, msg=None, *args, **kwargs):
        current = datetime.datetime.now()
        level = self.level.get('val') if isinstance(self.level, dict) else self.level
        output = f" [{self.level.get('desc')}] {msg} " if isinstance(self.level, dict) else f" {msg} "
        if len(args) > 0: output = '{a} {b}'.format(a=output, b=args)
        if len(kwargs) > 0: output = '{a} {b}'.format(a=output, b=kwargs)
        if level == logging.DEBUG:
            self.logger.debug(output)
        elif level == logging.INFO:
            self.logger.info(output)
        elif level == logging.WARNING:
            self.logger.warning(output)
        elif level == logging.ERROR:
            self.logger.error(output)
        elif level == logging.CRITICAL:
            self.logger.critical(output)

dump = ServerLogger(config=LOGGING_CONFIG, level=DEBUG_LARGEDATA)
debug = ServerLogger(config=LOGGING_CONFIG, level=logging.DEBUG)
info = ServerLogger(config=LOGGING_CONFIG, level=logging.INFO)
warning = ServerLogger(config=LOGGING_CONFIG, level=logging.WARNING)
error = ServerLogger(config=LOGGING_CONFIG, level=logging.ERROR)
critical = ServerLogger(config=LOGGING_CONFIG, level=logging.CRITICAL)
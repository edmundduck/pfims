import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import logging as logging
import logging.config as config

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.
LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s %(levelname)-8s %(message)s"
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

@anvil.server.callable
def log(name, message, level='DEBUG'):
    config.dictConfig(LOGGING_CONFIG)
    log = logging.getLogger(name)
    if level == 'DEBUG':
        log.debug(message)
    elif level == 'INFO':
        log.info(message)
    elif level == 'WARNING':
        log.warning(message)
    elif level == 'ERROR':
        log.error(message)
    elif level == 'CRITICAL':
        log.critical(message)

import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import logging

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.

logconf = logging.dictConfig({
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
            "stream": sys.stdout
        }
    },
    "loggers": {
        "": {
            "level": "INFO",
            "handlers": ["console"]
        }
    }
})
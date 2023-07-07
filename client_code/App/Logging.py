import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import datetime
# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

# Constants
DEBUG = 'DEBUG'
INFO = 'INFO'
WARNING = 'WARNING'
ERROR = 'ERROR'
CRITICAL = 'CRITICAL'

class Logger():
    def __init__(self, config, level=INFO, enabled=True):
        self.datefmt = config.datefmt
        self.level = level
        self.enabled = enabled

    def log(self, message):
        if self.enabled:
            current = datetime.datetime.now()
            print(f"{current.strftime(self.datefmt)} - {self.level} - {message}")

class LoggerConfig():
    def __init__(self, datefmt='%Y-%m-%d %H:%M:%S'):
        self.datefmt = datefmt

config = LoggerConfig()

debug = Logger(config=config, level=DEBUG, enabled=False)
info = Logger(config=config)
warning = Logger(config=config, level=WARNING)
error = Logger(config=config, level=ERROR)
critical = Logger(config=config, level=CRITICAL)

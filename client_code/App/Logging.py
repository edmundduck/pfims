import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import datetime
# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

import datetime

# Constants
DEBUG = 'DEBUG'
INFO = 'INFO'
WARNING = 'WARNING'
ERROR = 'ERROR'
CRITICAL = 'CRITICAL'
loglevel = {
    DEBUG: 0,
    INFO: 1,
    WARNING: 2,
    ERROR: 3,
    CRITICAL: 4
}

class Logger():
    def __init__(self, config, level):
        self.datefmt = config.datefmt
        self.default = config.default
        self.level = level

    def log(self, msg=None, *args, **kwargs):
        if loglevel.get(self.level) >= loglevel.get(self.default):
            current = datetime.datetime.now()
            output = f"{current.strftime(self.datefmt)} - {self.level} - {msg} "
            if len(args) > 0: output = "{a} {b}".format(a=output, b=args)
            if len(kwargs) > 0: output = "{a} {b}".format(a=output, b=kwargs)
            print(output)

class LoggerConfig():
    def __init__(self, datefmt='%Y-%m-%d %H:%M:%S', default=INFO):
        self.datefmt = datefmt
        self.default = default

config = LoggerConfig(default=DEBUG)

debug = Logger(config=config, level=DEBUG)
info = Logger(config=config, level=INFO)
warning = Logger(config=config, level=WARNING)
error = Logger(config=config, level=ERROR)
critical = Logger(config=config, level=CRITICAL)
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import datetime
# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

# Constants
DEBUG_LARGEDATA = { 'val':5, 'desc':'DUMP' }
DEBUG = { 'val':10, 'desc':'DEBUG' }
INFO = { 'val':20, 'desc':'INFO' }
WARNING = { 'val':30, 'desc':'WARNING' }
ERROR = { 'val':40, 'desc':'ERROR' }
CRITICAL = { 'val':50, 'desc':'CRITICAL' }

class Logger():
    def __init__(self, config, level):
        self.datefmt = config.datefmt
        self.default = config.default
        self.level = level

    def log(self, msg=None, *args, **kwargs):
        if self.level.get('val') >= self.default.get('val'):
            current = datetime.datetime.now()
            output = f" {current.strftime(self.datefmt)} [{self.level.get('desc')}] {msg} "
            if len(args) > 0: output = "{a} {b}".format(a=output, b=args)
            if len(kwargs) > 0: output = "{a} {b}".format(a=output, b=kwargs)
            print(output)

class LoggerConfig():
    def __init__(self, datefmt='%Y-%m-%d %H:%M:%S', default=INFO):
        self.datefmt = datefmt
        self.default = default

config = LoggerConfig(default=DEBUG_LARGEDATA)

dump = Logger(config=config, level=DEBUG_LARGEDATA)
debug = Logger(config=config, level=DEBUG)
info = Logger(config=config, level=INFO)
warning = Logger(config=config, level=WARNING)
error = Logger(config=config, level=ERROR)
critical = Logger(config=config, level=CRITICAL)
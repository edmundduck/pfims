import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import datetime

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

# Constants
TRACE = { 'val':5, 'desc':'TRACE' }
DEBUG = { 'val':10, 'desc':'DEBUG' }
INFO = { 'val':20, 'desc':'INFO' }
WARNING = { 'val':30, 'desc':'WARNING' }
ERROR = { 'val':40, 'desc':'ERROR' }
CRITICAL = { 'val':50, 'desc':'CRITICAL' }

# Config - Customize the log level required here
def get_log_level():
    settings = anvil.server.call('select_settings')
    return WARNING if settings.get('logging_level', None) is None else settings.get('logging_level')
    
LOG_LEVEL = get_log_level()

class ClientLogger():
    def __init__(self, config, level):
        self.datefmt = config.datefmt
        self.default = config.default
        self.level = level

    def log_function(self, func):
        def wrapper(*args, **kwargs):
            # Log the function call
            self.log("Client function %s starts ..." % func.__qualname__)
            # Call the original function
            result = func(*args, **kwargs)
            # Log the function return value
            self.log("Client function %s returned: %s ///" % (func.__qualname__, result))
            return result
        return wrapper

    def log(self, msg=None, *args, **kwargs):
        if self.level.get('val') >= self.default.get('val'):
            current = datetime.datetime.now()
            output = f"[C] {current.strftime(self.datefmt)} [{self.level.get('desc')}] {msg} "
            if len(args) > 0: output = "{a} {b}".format(a=output, b=args)
            if len(kwargs) > 0: output = "{a} {b}".format(a=output, b=kwargs)
            print(output)

class ClientLoggerConfig():
    def __init__(self, datefmt='%Y-%m-%d %H:%M:%S', default=INFO):
        self.datefmt = datefmt
        self.default = default

config = ClientLoggerConfig(datefmt='%Y-%m-%d %H:%M:%S,%f', default=LOG_LEVEL)

trace = ClientLogger(config=config, level=TRACE)
debug = ClientLogger(config=config, level=DEBUG)
info = ClientLogger(config=config, level=INFO)
warning = ClientLogger(config=config, level=WARNING)
error = ClientLogger(config=config, level=ERROR)
critical = ClientLogger(config=config, level=CRITICAL)
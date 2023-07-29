import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import datetime

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

# Config - Customize the log level required here
class ClientLoggerLevel:
    TRACE = { 'val':5, 'desc':'TRACE' }
    DEBUG = { 'val':10, 'desc':'DEBUG' }
    INFO = { 'val':20, 'desc':'INFO' }
    WARNING = { 'val':30, 'desc':'WARNING' }
    ERROR = { 'val':40, 'desc':'ERROR' }
    CRITICAL = { 'val':50, 'desc':'CRITICAL' }

class ClientLogger:
    def __init__(self, config, default_level=ClientLoggerLevel.WARNING):
        self.datefmt = config.datefmt
        self.default_level = default_level

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

    def _log(self, level=None, msg=None, *args, **kwargs):
        if self.level.get('val') >= self.default_level.get('val'):
            current = datetime.datetime.now()
            output = f"[C] {current.strftime(self.datefmt)} [{self.level.get('desc')}] {msg} "
            if len(args) > 0: output = "{a} {b}".format(a=output, b=args)
            if len(kwargs) > 0: output = "{a} {b}".format(a=output, b=kwargs)
            print(output)

    def trace(self, msg=None, *args, **kwargs):
        self._log(self, ClientLoggerLevel.TRACE, msg, *args, **kwargs)

    def debug(self, msg=None, *args, **kwargs):
        self._log(self, ClientLoggerLevel.DEBUG, msg, *args, **kwargs)

    def info(self, msg=None, *args, **kwargs):
        self._log(self, ClientLoggerLevel.INFO, msg, *args, **kwargs)

    def warning(self, msg=None, *args, **kwargs):
        self._log(self, ClientLoggerLevel.WARNING, msg, *args, **kwargs)

    def error(self, msg=None, *args, **kwargs):
        self._log(self, ClientLoggerLevel.ERROR, msg, *args, **kwargs)

    def critical(self, msg=None, *args, **kwargs):
        self._log(self, ClientLoggerLevel.CRITICAL, msg, *args, **kwargs)

class ClientLoggerConfig:
    def __init__(self, config_dict):
        if config_dict:
            self.datefmt = config_dict.get('datefmt') if config_dict.get('datefmt') else '%Y-%m-%d %H:%M:%S'
            # self.msgfmt = config_dict.get('msgfmt') if config_dict.get('msgfmt') else '[C]'

config = ClientLoggerConfig({
    'datefmt': '%Y-%m-%d %H:%M:%S,%f'
})

logger = ClientLogger(config=config, level=ClientLoggerLevel.INFO)
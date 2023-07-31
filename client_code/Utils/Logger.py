import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import datetime
import time

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

class ClientLoggerLevel:
    def __init__(self, val, desc):
        self.val = val
        self.desc = desc

TRACE = ClientLoggerLevel(5, 'TRACE')
DEBUG = ClientLoggerLevel(10, 'DEBUG')
INFO = ClientLoggerLevel(20, 'INFO')
WARNING = ClientLoggerLevel(30, 'WARNING')
ERROR = ClientLoggerLevel(40, 'ERROR')
CRITICAL = ClientLoggerLevel(50, 'CRITICAL')
# ** Config - Customize the application logging level below **
# ** User logging level, if exists, overrides application logging level **
APP_LOGGING_LVL = INFO
# ** Config - Customize the application logging level END **

class ClientLoggerConfig:
    DEFAULT_CONFIG = {
        'datefmt': '%Y-%m-%d %H:%M:%S,%f'
    }

class ClientLogger:
    def __init__(self, config=ClientLoggerConfig.DEFAULT_CONFIG, logging_level=APP_LOGGING_LVL):
        self.datefmt = config.get('datefmt')
        self.set_level()

    def set_level(self):
        # from .Caching import get_client_loglevel, set_client_loglevel, client_loglevel_reset
        # TODO implement caching (have to resolve the circular import issue first ...)
        # self.logging_level = get_client_loglevel()
        # if self.logging_level is None:
        #     self.debug(f"Client logging_level is None ...")
            userlevel = anvil.server.call('set_user_logging_level')
            self.logging_level = userlevel if userlevel is not None else self.logging_level
            # set_client_loglevel(self.logging_level)

    def log_function(self, func):
        def wrapper(*args, **kwargs):
            # Log the function call
            self.debug("///// Client function %s starts /////" % func.__qualname__)
            # Call the original function
            result = func(*args, **kwargs)
            # Log the function return value
            self.debug("///// Client function %s returned: %s /////" % (func.__qualname__, result))
            return result
        return wrapper

    def _log(self, level, msg=None, *args, **kwargs):
        baselvl = self.logging_level.val if isinstance(self.logging_level, ClientLoggerLevel) else self.logging_level
        loglvl = level.val if isinstance(level, ClientLoggerLevel) else level
        loglvldesc = level.desc if isinstance(level, ClientLoggerLevel) else loglvl
        if loglvl >= baselvl:
            current = datetime.datetime.now()
            output = f"[C] {current.strftime(self.datefmt)} [{loglvldesc}] {msg} "
            if len(args) > 0: output = "{a} {b}".format(a=output, b=args)
            if len(kwargs) > 0: output = "{a} {b}".format(a=output, b=kwargs)
            print(output)

    def trace(self, msg=None, *args, **kwargs):
        self._log(TRACE, msg, *args, **kwargs)

    def debug(self, msg=None, *args, **kwargs):
        self._log(DEBUG, msg, *args, **kwargs)

    def info(self, msg=None, *args, **kwargs):
        self._log(INFO, msg, *args, **kwargs)

    def warning(self, msg=None, *args, **kwargs):
        self._log(WARNING, msg, *args, **kwargs)

    def error(self, msg=None, *args, **kwargs):
        self._log(ERROR, msg, *args, **kwargs)

    def critical(self, msg=None, *args, **kwargs):
        self._log(CRITICAL, msg, *args, **kwargs)

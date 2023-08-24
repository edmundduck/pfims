import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import logging as logging
import logging.config as config
import datetime
import time
import pytz
import psycopg2
import psycopg2.extras

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.

class ServerLoggerLevel:
    DEFAULT_LVL = logging.INFO
    TRACE = {'val':logging.DEBUG-5, 'desc':'TRACE'}

# Suppose the timezone doesn't have to be configured further as logging is for internal use only
# Ref: https://stackoverflow.com/questions/32402502/how-to-change-the-time-zone-in-python-logging
class TimeZoneFormatter(logging.Formatter):
    converter = lambda *args: datetime.datetime.now(pytz.timezone('Europe/London')).timetuple()
    
class ServerLoggerConfig:
    DEFAULT_LOGGING_CONFIG = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'standard': {
                    '()': TimeZoneFormatter,
                    'format': '[S] %(asctime)s [%(levelname)s] %(message)s',
                    'datefmt': '%Y-%m-%d %H:%M:%S'
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

class ServerLogger:
    # Cannot put function loglevel in level argument otherwise will cause nested loop (reason unknown)
    def __init__(self, config=ServerLoggerConfig.DEFAULT_LOGGING_CONFIG, level=ServerLoggerLevel.DEFAULT_LVL):
        self.logger = logging.getLogger(__name__)
        self.default_level = level
        logging.addLevelName(ServerLoggerLevel.TRACE.get('val'), ServerLoggerLevel.TRACE.get('desc'))
        logging.config.dictConfig(config)
        # ** NOTE **
        # If set level is enabled in __init__, server session is NoneType (but eval it is not None which looks like a bug!!)
        # and cannot proceed forward, thus these 2 lines are placed in a separate function which is called everytime when log happens
        # **********
        # userlevel = anvil.server.session.get('loglevel')
        # self.logger.setLevel(userlevel if userlevel is not None else self.default_level)

    def set_level(self):
        userlevel = anvil.server.session.get('loglevel')
        self.logger.setLevel(userlevel if userlevel is not None else self.default_level)

    def log_function(self, func):
        def wrapper(*args, **kwargs):
            if self.logger.level == 0: self.set_level()
            # Log the function call
            self.trace("***** Server function %s starts *****" % func.__qualname__)
            start = time.time()
            # Call the original function
            result = func(*args, **kwargs)
            end = time.time()
            # Log the function return value
            self.trace("***** Server function %s returned (%s sec): %s *****" % (func.__qualname__, end - start, result))
            return result
        return wrapper

    def trace(self, msg=None, *args, **kwargs):
        if self.logger.level == 0: self.set_level()
        self.logger.log(ServerLoggerLevel.TRACE.get('val'), msg, *args, **kwargs)

    def debug(self, msg=None, *args, **kwargs):
        if self.logger.level == 0: self.set_level()
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg=None, *args, **kwargs):
        if self.logger.level == 0: self.set_level()
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg=None, *args, **kwargs):
        if self.logger.level == 0: self.set_level()
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg=None, *args, **kwargs):
        if self.logger.level == 0: self.set_level()
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg=None, *args, **kwargs):
        if self.logger.level == 0: self.set_level()
        self.logger.critical(msg, *args, **kwargs)

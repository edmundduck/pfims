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
    """
    All the server logger level relevant settings are stored here.
    """
    DEFAULT_LVL = logging.INFO
    TRACE = {'val':logging.DEBUG-5, 'desc':'TRACE'}

# Ref: https://stackoverflow.com/questions/32402502/how-to-change-the-time-zone-in-python-logging
class TimeZoneFormatter(logging.Formatter):
    """
    Time zone converter.
    
    Suppose the timezone doesn't have to be configured further as logging is for internal use only
    """
    converter = lambda *args: datetime.datetime.now(pytz.timezone('Europe/London')).timetuple()
    
class ServerLoggerConfig:
    """
    All the server logger configuration are stored here.
    """
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
                    'level': 'INFO',
                    'handlers': ['console']
                }
            }
        }

class ServerLogger:
    """
    Server logger logic which is written based on Python logger.
    """
    # Cannot put function loglevel in level argument otherwise will cause nested loop (reason unknown)
    def __init__(self, config=ServerLoggerConfig.DEFAULT_LOGGING_CONFIG, level=ServerLoggerLevel.DEFAULT_LVL):
        self.logger = logging.getLogger(__name__)
        self.default_level = level
        logging.addLevelName(ServerLoggerLevel.TRACE.get('val'), ServerLoggerLevel.TRACE.get('desc'))
        logging.config.dictConfig(config)
        self.logger.setLevel(self.default_level)
        # ** NOTE **
        # If set level is enabled in __init__, server session is NoneType (but eval it is not None which looks like a bug!!)
        # and cannot proceed forward, thus these 2 lines are placed in a separate function which is called everytime when log happens
        # **********
        # userlevel = anvil.server.session.get('loglevel')
        # self.logger.setLevel(userlevel if userlevel is not None else self.default_level)

    def set_level(self):
        """
        Set the logger level from Anvil server session which was loaded when user logs on.
        """
        userlevel = anvil.server.session.get('loglevel')
        self.logger.setLevel(userlevel if userlevel is not None else self.default_level)

    def log_function(self, func):
        """
        A wrapper function to be used as decorator to log a function entry and exit with elapsed time.
    
        Parameters:
            func (function): The actual function to execute.
    
        Returns:
            wrapper (function): The wrapper function.
        """
        def wrapper(*args, **kwargs):
            self.set_level()
            # Log the function call
            self.debug("***** Server function %s starts *****" % func.__qualname__)
            start = time.time()
            # Call the original function
            result = func(*args, **kwargs)
            end = time.time()
            # Log the function return value
            self.debug("***** Server function %s returned (%s sec): %s *****" % (func.__qualname__, end - start, result))
            return result
        return wrapper

    def log(self, level, msg=None, *args, **kwargs):
        """
        Log the message together with list arguments and/or key arguments.
    
        Parameters:
            level (string): Log level.
            msg (string): Log message.
        """
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)
        self.set_level()
        self.logger.log(level, "".join((msg, signature)))
        
    def trace(self, msg=None, *args, **kwargs):
        """
        Log message in trace level.
    
        Parameters:
            msg (string): Log message.
        """
        self.log(ServerLoggerLevel.TRACE.get('val'), msg, *args, **kwargs)

    def debug(self, msg=None, *args, **kwargs):
        """
        Log message in debug level.
    
        Parameters:
            msg (string): Log message.
        """
        self.log(logging.DEBUG, msg, *args, **kwargs)

    def info(self, msg=None, *args, **kwargs):
        """
        Log message in info level.
    
        Parameters:
            msg (string): Log message.
        """
        self.log(logging.INFO, msg, *args, **kwargs)

    def warning(self, msg=None, *args, **kwargs):
        """
        Log message in warning level.
    
        Parameters:
            msg (string): Log message.
        """
        self.log(logging.WARNING, msg, *args, **kwargs)

    def error(self, err, msg=None, *args, **kwargs):
        """
        Log message in error level.
    
        Parameters:
            err (Exception): Exception.
            msg (string): Optional. Log message.
        """
        if msg:
            # errmsg = f"{err.__traceback__.tb_frame.f_code.co_filename}(Line {err.__traceback__.tb_lineno}): {__name__}.{type(err).__name__}: {err} {msg}"
            errmsg = f"{err} {msg}"
        else:
            # errmsg = f"{err.__traceback__.tb_frame.f_code.co_filename}(Line {err.__traceback__.tb_lineno}): {__name__}.{type(err).__name__}: {err}"
            errmsg = f"{err}"
        self.log(logging.ERROR, errmsg, *args, **kwargs)

    def critical(self, msg=None, *args, **kwargs):
        """
        Log message in critical level.
    
        Parameters:
            msg (string): Log message.
        """
        self.log(logging.CRITICAL, msg, *args, **kwargs)

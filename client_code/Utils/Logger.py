import anvil.server
import datetime
import time

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

class ClientLoggerLevel:
    def __init__(self, val, desc):
        self.val = val
        self.desc = desc

class ClientLoggerConfig:
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

    DEFAULT_CONFIG = {
        'datefmt': '%Y-%m-%d %H:%M:%S,%f'
    }

class ClientLogger:
    """
    Client logger logic which is written based on Python logger.
    """
    def __init__(self, config=ClientLoggerConfig.DEFAULT_CONFIG, logging_level=ClientLoggerConfig.APP_LOGGING_LVL):
        self.datefmt = config.get('datefmt')
        self.logging_level = logging_level
        self.set_level()

    def set_level(self):
        """
        Set the logger level from Global logging level cache which was loaded when user logs on.
        """
        from .. import Global
        userlevel = Global.settings.get_logging_level()
        self.logging_level = userlevel if userlevel is not None else self.logging_level

    def log_function(self, func):
        """
        A wrapper function to be used as decorator to log a function entry and exit with elapsed time.
    
        Parameters:
            func (function): The actual function to execute.
    
        Returns:
            wrapper (function): The wrapper function.
        """
        def wrapper(*args, **kwargs):
            # Log the function call
            self.debug("///// Client function %s starts /////" % func.__qualname__)
            start = time.time()
            # Call the original function
            result = func(*args, **kwargs)
            end = time.time()
            # Log the function return value
            self.debug("///// Client function %s returned (%s sec): %s /////" % (func.__qualname__, end - start, result))
            return result
        return wrapper

    def _log(self, level, msg=None, *args, **kwargs):
        """
        Log the message together with list arguments and/or key arguments.
    
        Parameters:
            level (string): Log level.
            msg (string): Optional. Log message.
        """
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
        """
        Log message in trace level.
    
        Parameters:
            msg (string): Optional. Log message.
        """
        self._log(ClientLoggerConfig.TRACE, msg, *args, **kwargs)

    def debug(self, msg=None, *args, **kwargs):
        """
        Log message in debug level.
    
        Parameters:
            msg (string): Optional. Log message.
        """
        self._log(ClientLoggerConfig.DEBUG, msg, *args, **kwargs)

    def info(self, msg=None, *args, **kwargs):
        """
        Log message in info level.
    
        Parameters:
            msg (string): Optional. Log message.
        """
        self._log(ClientLoggerConfig.INFO, msg, *args, **kwargs)

    def warning(self, msg=None, *args, **kwargs):
        """
        Log message in warning level.
    
        Parameters:
            msg (string): Optional. Log message.
        """
        self._log(ClientLoggerConfig.WARNING, msg, *args, **kwargs)

    def error(self, err, msg=None, *args, **kwargs):
        """
        Log message in error level.
    
        Parameters:
            err (Exception): Exception.
            msg (string): Optional. Log message.
        """
        if msg:
            errmsg = f"{err.__traceback__.tb_frame.f_code.co_filename}(Line {err.__traceback__.tb_lineno}): {__name__}.{type(err).__name__}: {err} {msg}"
        else:
            errmsg = f"{err.__traceback__.tb_frame.f_code.co_filename}(Line {err.__traceback__.tb_lineno}): {__name__}.{type(err).__name__}: {err}"
        self._log(ClientLoggerConfig.ERROR, errmsg, *args, **kwargs)

    def critical(self, msg=None, *args, **kwargs):
        """
        Log message in critical level.
    
        Parameters:
            msg (string): Optional. Log message.
        """
        self._log(ClientLoggerConfig.CRITICAL, msg, *args, **kwargs)

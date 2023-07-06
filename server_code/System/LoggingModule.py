import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import logging

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.

@anvil.server.callable
def logger(name):
    logger=logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # file_handler=logging.FileHandler('test.log')
    stream_handler=logging.StreamHandler()
    
    stream_formatter=logging.Formatter(
        '%(asctime)-15s %(__name__)s %(levelname)-8s %(message)s')
    # file_formatter=logging.Formatter(
        # "{'time':'%(asctime)s', 'name': '%(name)s', \
        # 'level': '%(levelname)s', 'message': '%(message)s'}"
    # )
    
    # file_handler.setFormatter(file_formatter)
    stream_handler.setFormatter(stream_formatter)
    
    # logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger
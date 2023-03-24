import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.
#
# To allow anvil.server.call() to call functions here, we mark
# them with @anvil.server.callable.
# Here is an example - you can replace it with your own:
#
# @anvil.server.callable
# def say_hello(name):
#   print("Hello, " + name + "!")
#   return 42
#

# Global variable
del_iid = []

@anvil.server.callable
# For debug print
def print_data_debug(message, debug_data):
    print('***[DEBUG]*** {}: {}'.format(message, debug_data))

@anvil.server.callable
# Add IID into the deletion list for delete journals function to process
def delete_row(iid):
    global del_iid
    del_iid.append(iid)
    print_data_debug("del_iid", del_iid)

@anvil.server.callable
# Reset the deletion list
def reset_delete():
    global del_iid
    del_iid = []
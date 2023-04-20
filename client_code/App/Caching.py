import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:
#
#    from . import Module1
#
#    Module1.say_hello()
#

accounts = None
labels = None
labels_dict = None

def get_caching_accounts():
    global accounts
    if accounts is None:
        accounts = anvil.server.call('generate_accounts_dropdown')
    return accounts

def reset_caching_accounts():
    global accounts
    accounts = None

def get_caching_labels_dropdown():
    global labels
    if labels is None:
        labels = anvil.server.call('generate_labels_dropdown')
    return labels

def reset_caching_labels():
    global labels
    labels = None
    labels_dict = None

def get_caching_labels_dict():
    global labels_dict
    if labels_dict is None:
        labels = anvil.server.call('generate_labels_dropdown')
        
    return labels_dict
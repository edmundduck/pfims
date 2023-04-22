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
labels_list = None

def get_caching_accounts():
    global accounts
    if accounts is None:
        accounts = anvil.server.call('generate_accounts_dropdown_only_id')
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
    labels_list = None

def get_caching_labels_list():
    global labels_list
    if labels_list is None:
        labels_list = anvil.server.call('generate_labels_list')
    return labels_list
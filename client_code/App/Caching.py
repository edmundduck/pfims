import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

accounts = None
labels = None
labels_list = None
exp_tbl_def = None
upload_action = None

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

def get_caching_exp_tbl_def():
    global exp_tbl_def
    if exp_tbl_def is None:
        exp_tbl_def = anvil.server.call('generate_expense_tbl_def_dropdown')
    return exp_tbl_def

def reset_caching_exp_tbl_def():
    global exp_tbl_def
    exp_tbl_def = None

def get_caching_upload_action():
    global upload_action
    if upload_action is None:
        upload_action = anvil.server.call('generate_upload_action_dropdown')
    return upload_action

def reset_caching_upload_action():
    global upload_action
    upload_action = None
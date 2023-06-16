import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

accounts = None
mapping_type = None
labels = None
labels_dict = None
labels_list = None
labels_mapping_action = None
exp_tbl_def = None
exp_tbl_def_dict = None
upload_action = None
upload_action_dict = None

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

def to_dict_caching_labels():
    global labels_dict
    if labels_dict is None:
        labels_dict = {}
        for i in get_caching_labels_dropdown():
            labels_dict[i[1]['id']] = i[1]['text']
    return labels_dict

def reset_caching_labels():
    global labels
    labels = None
    labels_dict = None
    labels_list = None

def get_caching_labels_list():
    global labels_list
    if labels_list is None:
        labels_list = anvil.server.call('generate_labels_list')
    return labels_list

def get_caching_labels_mapping_action_dropdown():
    global labels_mapping_action
    if labels_mapping_action is None:
        labels_mapping_action = anvil.server.call('generate_labels_mapping_action_dropdown')
    return labels_mapping_action

def reset_caching_labels_mapping_action_dropdown():
    global labels_mapping_action
    labels_mapping_action = None

def get_caching_exp_tbl_def():
    global exp_tbl_def
    if exp_tbl_def is None:
        exp_tbl_def = anvil.server.call('generate_expense_tbl_def_dropdown')
    return exp_tbl_def

def to_dict_caching_exp_tbl_def():
    global exp_tbl_def_dict
    if exp_tbl_def_dict is None:
        exp_tbl_def_dict = {}
        for i in get_caching_exp_tbl_def():
            exp_tbl_def_dict[i[1]['id']] = i[1]['text']
    return exp_tbl_def_dict

def reset_caching_exp_tbl_def():
    global exp_tbl_def
    exp_tbl_def = None

def get_caching_upload_action():
    global upload_action
    if upload_action is None:
        upload_action = anvil.server.call('generate_upload_action_dropdown')
    return upload_action

def to_dict_caching_upload_action():
    global upload_action_dict
    if upload_action_dict is None:
        upload_action_dict = {}
        for i in get_caching_upload_action():
            upload_action_dict[i[1]['id']] = i[1]['text']
    return upload_action_dict
    
def reset_caching_upload_action():
    global upload_action
    upload_action = None

def get_caching_mapping_type():
    global mapping_type
    if mapping_type is None:
        mapping_type = anvil.server.call('generate_mapping_type_dropdown')
    return mapping_type

def reset_caching_mapping_type():
    global mapping_type
    filter_type = None
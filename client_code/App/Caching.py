import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

cache_dict = {}
mapping_type = None
labels = None
labels_dict = None
labels_list = None
labels_mapping_action = None
exp_tbl_def = None
exp_tbl_def_dict = None
upload_action = None
upload_action_dict = None

def accounts_dropdown():
    return get_cache_dropdown(key='accounts', func='generate_accounts_dropdown')

def accounts_dict():
    return get_cache_dict(key='accounts', func='generate_accounts_dropdown')

def accounts_reset():
    clear_cache(key='accounts')

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
            # Case 001 - string dict key handling review
            labels_dict[str(eval(i[1])['id'])] = eval(i[1])['text']
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

def expense_tbl_def_dropdown():
    return get_cache_dropdown(key='expense_tbl_def', func='generate_expense_tbl_def_dropdown')

def expense_tbl_def_dict():
    return get_cache_dict(key='expense_tbl_def', func='generate_expense_tbl_def_dropdown')

def expense_tbl_def_reset():
    clear_cache(key='expense_tbl_def')

def upload_action_dropdown():
    return get_cache_dropdown(key='upload_action', func='generate_upload_action_dropdown')

def upload_action_dict():
    return get_cache_dict(key='upload_action', func='generate_upload_action_dropdown')
    
def upload_action_reset():
    clear_cache(key='upload_action')

def rule_mapping_filetype_dropdown():
    return get_cache_dropdown(key='rule_mapping_filetype', func='generate_mapping_type_dropdown')

def rule_mapping_filetype_reset():
    clear_cache(key='rule_mapping_filetype')

# TODO - to implement a global cache access function
def get_cache_dropdown(key, func):
    global cache_dict
    if cache_dict is None: cache_dict = {}
    result = cache_dict.get(key, None)
    if result is None:
        result = anvil.server.call(func)
        cache_dict[key] = result
    return result

def get_cache_dict(key, func):
    result = {}
    for i in get_cache_dropdown(key, func):
        if isinstance(i[1], dict):
            result[i[1]['id']] = i[1]['text']
        else:
            result[i[1][0]] = i[1][1]
    return result

def clear_cache(key):
    global cache_dict
    cache_dict[key] = None

def clearall_cache():
    global cache_dict
    cache_dict.clear()
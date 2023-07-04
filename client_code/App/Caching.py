import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

cache_dict = {}

def accounts_dropdown():
    return get_cache_dropdown(key='accounts', func='generate_accounts_dropdown')

def accounts_dict():
    return get_cache_dict(key='accounts', func='generate_accounts_dropdown')

def accounts_reset():
    clear_cache(key='accounts')

def labels_dropdown():
    return get_cache_dropdown(key='labels', func='generate_labels_dropdown')

def labels_dict():
    global cache_dict
    key='labels_dict'
    if cache_dict is None: cache_dict = {}
    result = cache_dict.get(key, {})
    if not result:
        for i in labels_dropdown():
            # Case 001 - string dict key handling review
            result[str(eval(i[1])['id'])] = eval(i[1])['text']
        cache_dict[key] = result
    return result

def labels_list():
    return get_cache_dropdown(key='labels_list', func='generate_labels_list')

def labels_reset():
    clear_cache(key='labels_list')
    clear_cache(key='labels_dict')
    clear_cache(key='labels')

def labels_mapping_action_dropdown():
    return get_cache_dropdown(key='labels_mapping_action', func='generate_labels_mapping_action_dropdown')

def labels_mapping_action_reset():
    clear_cache(key='labels_mapping_action')

def expense_tbl_def_dropdown():
    return get_cache_dropdown(key='expense_tbl_def', func='generate_expense_tbl_def_dropdown')

def expense_tbl_def_dict():
    return get_cache_dict(key='expense_tbl_def', func='generate_expense_tbl_def_dropdown')

def expense_tbl_def_reset():
    clear_cache(key='expense_tbl_def')

def mapping_rules_extra_action_dropdown():
    return get_cache_dropdown(key='mapping_rules_extra_action', func='generate_upload_action_dropdown')

def mapping_rules_extra_action_dict():
    return get_cache_dict(key='mapping_rules_extra_action', func='generate_upload_action_dropdown')
    
def mapping_rules_extra_action_reset():
    clear_cache(key='mapping_rules_extra_action')

def mapping_rules_filetype_dropdown():
    return get_cache_dropdown(key='mapping_rules_filetype', func='generate_mapping_type_dropdown')

def mapping_rules_filetype_reset():
    clear_cache(key='mapping_rules_filetype')

# Generic get and store database data as cache in a form of dropdown items
# @key = Key in string to access particular cache data
# @func = Function name in string which maps to a function in server module to get database data if corresponding cache is not found
def get_cache_dropdown(key, func):
    global cache_dict
    if cache_dict is None: cache_dict = {}
    result = cache_dict.get(key, None)
    if result is None:
        result = anvil.server.call(func)
        cache_dict[key] = result
    return result

# Generic get and store database data as cache in a form of dictionary
# @key = Key in string to access particular cache data
# @func = Function name in string which maps to a function in server module to get database data if corresponding cache is not found
def get_cache_dict(key, func):
    result = {}
    for i in get_cache_dropdown(key, func):
        result[i[1][0]] = i[1][1]
    return result

# Generic clear cache
# @key = Key in string to access particular cache data
def clear_cache(key):
    global cache_dict
    cache_dict[key] = None

# Generic clear all cache (all keys)
def clearall_cache():
    global cache_dict
    cache_dict.clear()
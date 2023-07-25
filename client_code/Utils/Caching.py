import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

cache_dict = {}

# Return a list for accounts dropdown for Expense Input and Upload
def accounts_dropdown():
    return get_cache('accounts', 'generate_accounts_dropdown')

# Return a dict for accounts for Expense Input and Upload
def accounts_dict():
    return get_cache_dict('accounts', 'generate_accounts_dropdown')

def accounts_reset():
    clear_cache('accounts')

# Return a list for labels dropdown for Expense Input and Upload
def labels_dropdown():
    return get_cache('labels', 'generate_labels_dropdown')

# Return a dict for labels for Expense Input and Upload
# Not using generic get_cache_dict function as it involves eval() issue requiring special handling
def labels_dict():
    global cache_dict
    key='labels_dict'
    if cache_dict is None: cache_dict = {}
    result = cache_dict.get(key, {})
    if not result:
        for i in labels_dropdown():
            # trace.log("item (i) in labels_dropdown=", i)
            # trace.log("eval(i[1])['id']=", eval(i[1])['id'])
            # trace.log("eval(i[1])['text']=", eval(i[1])['text'])
            # Case 001 - string dict key handling review
            result[str(eval(i[1])['id'])] = eval(i[1])['text']
        cache_dict[key] = result
    return result

def labels_list():
    return get_cache('labels_list', 'generate_labels_list')

def labels_reset():
    clear_cache('labels_list')
    clear_cache('labels_dict')
    clear_cache('labels')

# Return a list for labels mapping action dropdown for Expense Input and Upload
def labels_mapping_action_dropdown():
    return get_cache(key='labels_mapping_action', func='generate_labels_mapping_action_dropdown')

def labels_mapping_action_reset():
    clear_cache(key='labels_mapping_action')

# Return a list for expense table definition dropdown for Expense Input and Upload
def expense_tbl_def_dropdown():
    return get_cache(key='expense_tbl_def', func='generate_expense_tbl_def_dropdown')

# Return a dict for expense table definition for Expense Input and Upload
def expense_tbl_def_dict():
    return get_cache_dict(key='expense_tbl_def', func='generate_expense_tbl_def_dropdown')

def expense_tbl_def_reset():
    clear_cache(key='expense_tbl_def')

# Return a list for extra action dropdown for Expense Input and Upload
def mapping_rules_extra_action_dropdown():
    return get_cache(key='mapping_rules_extra_action', func='generate_upload_action_dropdown')

# Return a dict for extra action for Expense Input and Upload
def mapping_rules_extra_action_dict():
    return get_cache_dict(key='mapping_rules_extra_action', func='generate_upload_action_dropdown')
    
def mapping_rules_extra_action_reset():
    clear_cache(key='mapping_rules_extra_action')

# Return a list for file type dropdown for Expense Input and Upload
def mapping_rules_filetype_dropdown():
    return get_cache(key='mapping_rules_filetype', func='generate_mapping_type_dropdown')

def mapping_rules_filetype_reset():
    clear_cache(key='mapping_rules_filetype')

def search_interval_dropdown():
    return get_cache(key='search_interval', func='select_search_interval')

def search_interval_reset():
    clear_cache(key='search_interval')

def ccy_dropdown():
    return get_cache(key='ccy', func='generate_ccy_dropdown')

def ccy_reset():
    clear_cache(key='ccy')
    
# Add IID into the deletion list for delete journals / delete transactions function to process
def add_deleted_row(iid):
    global cache_dict
    key = 'delete_row_iid'
    if cache_dict is None: cache_dict = {}
    if cache_dict.get(key, None) is None:
        cache_dict[key] = [iid]
    else:
        cache_dict[key].append(iid)
    return cache_dict.get(key, [])

# Return IID of the deletion list for delete journals / delete transactions function to process
def get_deleted_row():
    global cache_dict
    key = 'delete_row_iid'
    if cache_dict is None: cache_dict = {}
    return cache_dict.get(key, [])
    
def deleted_row_reset():
    clear_cache(key='delete_row_iid')

def logging_level():
    settings = get_cache_dict(key='logging_level', func='select_settings')
    return settings.get('logging_level')

def logging_level_reset():
    clear_cache(key='logging_level')

# Generic get and store database data as cache in a form of dropdown items
# @key = Key in string to access particular cache data
# @func = Function name in string which maps to a function in server module to get database data if corresponding cache is not found
def get_cache(key, func, *args):
    # from . import Logger
    from .Logger import trace, debug, info, warning, error, critical
    from .Logger import 
    global cache_dict
    if cache_dict is None: cache_dict = {}
    if cache_dict.get(key, None) is None:
        cache_dict[key] = anvil.server.call(func, *args)
        debug.log(f"get_cache cache loaded (key={key}, func={func})")
    return cache_dict.get(key, None)

# Generic get and store database data as cache in a form of dictionary
# @key = Key in string to access particular cache data
# @func = Function name in string which maps to a function in server module to get database data if corresponding cache is not found
def get_cache_dict(key, func, *args):
    # from . import Logger
    from .Logger import trace, debug, info, warning, error, critical
    global cache_dict
    dict_key = "".join((key, '_dict'))
    if cache_dict.get(dict_key, None) is None:
        result = {}
        for i in get_cache(key, func, *args):
            result[i[1][0]] = i[1][1]
        cache_dict[dict_key] = result
        debug.log(f"get_cache_dict cache loaded (dict_key={dict_key}, func={func})")
    return cache_dict.get(dict_key, None)

# Generic clear cache
# @key = Key in string to access particular cache data
def clear_cache(key):
    # from . import Logger
    from .Logger import trace, debug, info, warning, error, critical
    global cache_dict
    cache_dict[key] = None
    cache_dict["".join((key, '_dict'))] = None
    debug.log(f"Cache clear (key={key})")

# Generic clear all cache (all keys)
def clearall_cache():
    global cache_dict
    cache_dict.clear()
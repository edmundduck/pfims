import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .Logger import ClientLogger

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

cache_dict = {}
logger = ClientLogger()

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
    logger.trace("cache_dict=", cache_dict)
    result = cache_dict.get(key, {}) or {}
    if not result:
        for i in labels_dropdown():
            logger.trace("item (i) in labels_dropdown=", i)
            logger.trace("eval(i[1])['id']=", eval(i[1])['id'])
            logger.trace("eval(i[1])['text']=", eval(i[1])['text'])
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

def expense_empty_record():
    """
    Return a copy of an empty ExpenseRecord object.

    A copy is required otherwise all new rows generated by Expense Record will have reference to the same object.

    Returns:
        ExpenseRecord object: Return a copy of the empty ExpenseRecord object.
    """
    emptyrcd = get_cache(key='expense_empty_rcd', func='emptyexprecord')
    return emptyrcd.copy()
    
# Return a dict for expense table definition for Expense Input and Upload
def expense_tbl_def_dict():
    return get_cache_dict(key='expense_tbl_def', func='generate_expense_tbl_def_dropdown')

# Return a complete tuple key based on ID which is a part of the key in a list for expense table definition dropdown
def expense_tbl_def_getkey(id):
    return get_key_from_cache(id, get_cache(key='expense_tbl_def', func='generate_expense_tbl_def_dropdown'))
        
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

def set_client_loglevel(level):
    global cache_dict
    key = 'cloglevel'
    if cache_dict is None: cache_dict = {}
    cache_dict[key] = level

# Return the client logging level
def get_client_loglevel():
    global cache_dict
    key = 'cloglevel'
    if cache_dict is None: cache_dict = {}
    return cache_dict.get(key, None)

def client_loglevel_reset():
    clear_cache(key='cloglevel')
    
def set_cache(key, data, *args):
    """
    Generic store data as cache.

    Parameters:
        key (string): Key in string to store particular cache data.
        data (list): Data to store inside cache.
    """
    global cache_dict
    if cache_dict is None: cache_dict = {}
    cache_dict[key] = data
    logger.trace(f"Cache loaded by set_cache (key={key}) - List? {isinstance(data, list)}")
        
def get_cache(key, func, *args):
    """
    Generic get and store data in a form of list per function call as cache.

    Parameters:
        key (string): Key in string to access and store particular cache data.
        func (function): Function name in string which maps to a function in server module to get database data if corresponding cache is not found.

    Returns:
        cache_dict.get (list): Cache in list given the provided key
    """
    global cache_dict
    if cache_dict.get(key, None) is None:
        set_cache(key, data=anvil.server.call(func, *args))
        logger.debug(f"Cache loaded by get_cache (key={key}, func={func})")
    return cache_dict.get(key, None)

def get_cache_dict(key, func, *args):
    """
    Generic get and store data in a form of dictionary per function call as cache.

    Parameters:
        key (string): Key in string to access and store particular cache data. Suffix for dictionary will be auto appended to distinguish from cache in list.
        func (function): Function name in string which maps to a function in server module to get database data if corresponding cache is not found.

    Returns:
        cache_dict.get (dict): Cache in dict given the provided key
    """
    global cache_dict
    dict_key = "".join((key, '_dict'))
    if cache_dict.get(dict_key, None) is None:
        result = {}
        for i in get_cache(key, func, *args):
            result[i[1][0]] = i[1][1]
        set_cache(dict_key, result)
        logger.debug(f"Cache loaded by get_cache_dict (dict_key={dict_key}, func={func})")
    return cache_dict.get(dict_key, None)

# Generic clear cache
# @key = Key in string to access particular cache data
def clear_cache(key):
    global cache_dict
    key_to_clear = [key, "".join((key, '_dict'))]
    for k in key_to_clear:
        if k in cache_dict:
            del cache_dict[k]
            logger.debug(f"Cleared cache key={k}")
        else:
            logger.debug(f"Cache key={k} does not exist")    

# Generic clear all cache (all keys)
def clearall_cache():
    global cache_dict
    cache_dict.clear()

# Return a complete tuple key based on ID which is a part of the key in a list
def get_key_from_cache(id, func):
    li = func
    if any(isinstance(i, list) for i in li):
        return next((item[1] for item in li if id in item[1]), None)
        
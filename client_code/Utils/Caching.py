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
        
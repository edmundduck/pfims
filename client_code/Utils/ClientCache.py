import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .Logger import ClientLogger

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

class ClientCache:

    cache_dict = {}
    logger = ClientLogger()
    
    def __init__(self, funcname):
        self.funcname = funcname
        if cache_dict.get(funcname, None) is None:
            self.cache_dict[funcname] = anvil.server.call(funcname)

    def set_cache(self, key, data, *args):
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
            
    def get_cache(self):
        """
        Generic get cache data in a form of list.
    
        Returns:
            cache_dict.get (list): Cache in list given the provided key.
        """
        global cache_dict
        return cache_dict.get(self.funcname, None)
    
    def get_cache_dict(self, key, func, *args):
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
    def clear_cache(self, key):
        global cache_dict
        key_to_clear = [key, "".join((key, '_dict'))]
        for k in key_to_clear:
            if k in cache_dict:
                del cache_dict[k]
                logger.debug(f"Cleared cache key={k}")
            else:
                logger.debug(f"Cache key={k} does not exist")    
    

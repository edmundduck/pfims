import anvil.server
from .Constants import CacheDropdown
from .Logger import ClientLogger
from ..Entities.CacheListNode import DoubleLinkedList

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

# The logger cannot be placed inside __init__, otherwise performance will be dragged down dramatically.
logger = ClientLogger()

@anvil.server.portable_class
class ClientCache:

    # Class variable to store cache
    cache_list = DoubleLinkedList()

    def __init__(self, funcname):
        """
        Initialize the cache by either running as a server function or creating data manually.

        If the function name which is a parameter is not a valid server function name, NoServerFunctionError will throw.
        Then the cache will use the invalid 'function name' as the key of cache and load data which is an optional parameter into it.

        Parameters:
            funcname (string): A server function name or a string as cache key (invalid function name).
            data (any Object): Data to load manually if funcname is an invalid function name.
        """
        self.name = funcname

    def __str__(self):
        return "Cache {0} name:{1} includes -\n{2}".format(
            self.__class__,
            self.name,
            str(ClientCache.cache_list)
        )
        
    def is_empty(self):
        """
        Check if the cache is empty.
    
        Returns:
            boolean: Return True if the cache is empty.
        """
        if self.name is None or ClientCache.cache_list.loc(self.name) < 0:
            return True
        return False
    
    def get_cache(self):
        """
        Generic get cache data.
    
        Returns:
            ClientCache.cache_dict.get (list): Cache in list given the provided key.
        """
        data = ClientCache.cache_list.pop(self.name)
        if data:
            ClientCache.cache_list.add_to_head(self.name, data)
            logger.debug(f"Data {self.name} retrieved from cache.")
        return data
    
    def set_cache(self, data):
        """
        Generic set cache data.
    
        Parameters:
            data (any Object): Data to load manually.
        """
        ClientCache.cache_list.add_to_head(self.name, data)
        logger.debug(f"Cache {self.name} set manually from set_cache.")
        return data
    
    def clear_cache(self):
        """
        Generic clear cache to force the cache to retrieve the latest content in later get cache runs.
        """
        logger.debug(f"Cache {self.name} cleared.")
        return ClientCache.cache_list.pop(self.name)

class ClientDropdownCache(ClientCache):
    def __init__(self, funcname):
        super().__init__(funcname)

    def get_cache(self):
        result = None
        mapping = CacheDropdown.DROPDOWN_MAPPPING.get(self.name, None)
        if mapping:
            func, transform = mapping
            if self.is_empty():
                result = transform(self.set_cache(anvil.server.call(func)))
            else:
                cache = super(ClientDropdownCache, self).get_cache()
                result = transform(cache)
        return result

    def get_complete_key(self, partial_key):
        """
        Return a complete key based on a partial key which is a part of the key in a list.
    
        Returns:
            string: A complete key, otherwise the original partial key if not found.
        """
        cache = ClientCache.cache_list.pop(self.name)
        mapping = CacheDropdown.DROPDOWN_MAPPPING.get(self.name, None)
        if mapping:
            _, transform = mapping
            data = transform(cache)
        else:
            data = cache
        if data is not None:
            if partial_key and any(isinstance(i, (list, tuple)) for i in data):
                return next((item[1] for item in data if partial_key in item[1]), partial_key)
            else:
                return partial_key
        return partial_key

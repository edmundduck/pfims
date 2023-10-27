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
    cache_dict = {}
    cache_list = DoubleLinkedList()

    # def __init__(self, funcname, data=None):
    #     """
    #     Initialize the cache by either running as a server function or creating data manually.

    #     If the function name which is a parameter is not a valid server function name, NoServerFunctionError will throw.
    #     Then the cache will use the invalid 'function name' as the key of cache and load data which is an optional parameter into it.

    #     Parameters:
    #         funcname (string): A server function name or a string as cache key (invalid function name).
    #         data (any Object): Data to load manually if funcname is an invalid function name.
    #     """
    #     self.name = funcname
    #     if ClientCache.cache_dict.get(funcname, None) is None:
    #         if data is not None:
    #             ClientCache.cache_dict[funcname] = data
    #             logger.debug(f"Cache {self.name} initiated manually.")
    #         else:
    #             try:
    #                 ClientCache.cache_dict[funcname] = anvil.server.call(funcname)
    #                 logger.debug(f"Cache {self.name} initiated by calling function.")
    #             except (anvil.server.NoServerFunctionError) as err:
    #                 logger.warning(f"{funcname} cannot be found. Client cache cannot be initiated.")

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
            ClientCache.cache_dict.get(self.name, None)
        )
        
    # def is_empty(self):
    #     """
    #     Check if the cache is empty.
    
    #     Returns:
    #         boolean: Return True if the cache is empty.
    #     """
    #     if self.name is None or ClientCache.cache_dict.get(self.name, None) is None:
    #         return True
    #     return False

    def is_empty(self):
        """
        Check if the cache is empty.
    
        Returns:
            boolean: Return True if the cache is empty.
        """
        if self.name is None or ClientCache.cache_list.loc(self.name) < 0:
            return True
        return False
    
    # def get_cache(self):
    #     """
    #     Generic get cache data.
    
    #     Returns:
    #         ClientCache.cache_dict.get (list): Cache in list given the provided key.
    #     """
    #     if ClientCache.cache_dict.get(self.name, None) is None:
    #         try:
    #             ClientCache.cache_dict[self.name] = anvil.server.call(self.name)
    #             logger.debug(f"Cache {self.name} initiated from get_cache.")
    #         except (anvil.server.NoServerFunctionError) as err:
    #             logger.debug(f"Cache {self.name} cannot be initiated as function. No data retrieved.")
    #     return ClientCache.cache_dict.get(self.name, None)
    
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
        # if ClientCache.cache_dict.get(self.name, None) is None:
        #     try:
        #         ClientCache.cache_dict[self.name] = anvil.server.call(self.name)
        #         logger.debug(f"Cache {self.name} initiated from get_cache.")
        #     except (anvil.server.NoServerFunctionError) as err:
        #         logger.debug(f"Cache {self.name} cannot be initiated as function. No data retrieved.")
        return data
    
    # def set_cache(self, data):
    #     """
    #     Generic set cache data.
    
    #     Parameters:
    #         data (any Object): Data to load manually.
    #     """
    #     ClientCache.cache_dict[self.name] = data
    #     logger.debug(f"Cache {self.name} set manually from set_cache.")
    
    def set_cache(self, data):
        """
        Generic set cache data.
    
        Parameters:
            data (any Object): Data to load manually.
        """
        ClientCache.cache_list.add_to_head(self.name, data)
        logger.debug(f"Cache {self.name} set manually from set_cache.")
        return data
    
    # def clear_cache(self):
    #     """
    #     Generic clear cache to force the cache to retrieve the latest content in later get cache runs.
    #     """
    #     if ClientCache.cache_dict.get(self.name, None):
    #         del ClientCache.cache_dict[self.name]
    #     logger.debug(f"Cache {self.name} cleared.")

    def clear_cache(self):
        """
        Generic clear cache to force the cache to retrieve the latest content in later get cache runs.
        """
        logger.debug(f"Cache {self.name} cleared.")
        return ClientCache.cache_list.pop(self.name)

    # def get_complete_key(self, partial_key):
    #     """
    #     Return a complete key based on a partial key which is a part of the key in a list.
    
    #     Returns:
    #         string: A complete key, otherwise the original partial key if not found.
    #     """
    #     if ClientCache.cache_dict.get(self.name, None) is not None:
    #         cache = ClientCache.cache_dict.get(self.name, None)
    #         if partial_key and any(isinstance(i, (list, tuple)) for i in cache):
    #             return next((item[1] for item in cache if partial_key in item[1]), partial_key)
    #         else:
    #             return partial_key
    #     return partial_key

    def get_complete_key(self, partial_key):
        """
        Return a complete key based on a partial key which is a part of the key in a list.
    
        Returns:
            string: A complete key, otherwise the original partial key if not found.
        """
        cache = ClientCache.cache_list.pop(self.name)
        if cache is not None:
            if partial_key and any(isinstance(i, (list, tuple)) for i in cache):
                return next((item[1] for item in cache if partial_key in item[1]), partial_key)
            else:
                return partial_key
        return partial_key

class ClientDropdownCache(ClientCache):
    def get_cache(self):
        result = None
        mapping = CacheDropdown.DROPDOWN_MAPPPING.get(self.name, None)
        if mapping:
            func, transform = mapping
            if self.is_empty():
                result = transform(self.set_cache(anvil.server.call(func)))
            else:
                cache = super().get_cache()
                result = transform(cache)
        return result

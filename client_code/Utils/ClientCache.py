import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .Logger import ClientLogger

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

class ClientCache:

    # Class variable to store cache
    cache_dict = {}

    def __init__(self, funcname, data=None):
        self.name = funcname
        self.logger = ClientLogger()
        if ClientCache.cache_dict.get(funcname, None) is None:
            try:
                ClientCache.cache_dict[funcname] = anvil.server.call(funcname)
                self.logger.debug(f"Cache {self.name} (function) initiated.")
            except (anvil.server.NoServerFunctionError) as err:
                ClientCache.cache_dict[funcname] = data
                self.logger.debug(f"Cache {self.name} (manual) initiated.")

    def is_empty(self):
        """
        Check if the cache is empty.
    
        Returns:
            boolean: Return True if the cache is empty.
        """
        if self.name is None or ClientCache.cache_dict.get(self.name, None) is None:
            return True
        return False
    
    def get_cache(self):
        """
        Generic get cache data.
    
        Returns:
            ClientCache.cache_dict.get (list): Cache in list given the provided key.
        """
        print("//DEBUG// cache_dict=", ClientCache.cache_dict)
        if ClientCache.cache_dict.get(self.name, None) is None:
            ClientCache.cache_dict[self.name] = anvil.server.call(self.name)
            self.logger.debug(f"Cache {self.name} initiated from get_cache.")
        return ClientCache.cache_dict.get(self.name, None)
    
    def clear_cache(self):
        """
        Generic clear cache to force the cache to retrieve the latest content in later get cache runs.
        """
        del ClientCache.cache_dict[self.name]
        self.logger.debug(f"Cache {self.name} cleared.")

    def get_complete_key(self, partial_key):
        """
        Return a complete key based on a partial key which is a part of the key in a list.
    
        Returns:
            string: A complete key, otherwise the original partial key if not found.
        """
        if ClientCache.cache_dict.get(self.name, None) is not None:
            cache = ClientCache.cache_dict.get(self.name, None)
            if any(isinstance(i, list) for i in cache):
                return next((item[1] for item in cache if partial_key in item[1]), None)
            else:
                return partial_key
        return partial_key        
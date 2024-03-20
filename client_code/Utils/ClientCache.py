import anvil.server
from .Constants import CacheDropdown
from .Logger import ClientLogger
from ..Entities.CacheListNode import DoubleLinkedList
from .. import Global

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

# The logger cannot be placed inside __init__, otherwise performance will be dragged down dramatically.
logger = ClientLogger()

class ClientCache:

    # Class variable to store cache
    cache_list = DoubleLinkedList()

    def __init__(self, key):
        """
        Client cache initialization.

        Parameters:
            key (string): A key for client cache object.
        """
        self.name = key
        self.userid = Global.userid

    def __str__(self):
        """
        String presentation of the client cache object.

        Returns:
            string: The string presentation of the client cache object for logger print out.
        """
        return "Cache {0} name:{1} owned by: {3} includes -\n{2}".format(
            self.__class__,
            self.name,
            str(ClientCache.cache_list),
            self.userid
        )
        
    def is_empty(self):
        """
        Check if the cache is empty.
    
        Returns:
            boolean: Return True if the cache is empty.
        """
        if self.name is None or ClientCache.cache_list.loc(self.name) < 0:
            return True
        if ClientCache.cache_list.peek(self.name).get_value() is None:
            return True
        return False
    
    def is_expired(self):
        """
        Check if the cache is expired.
    
        Returns:
            boolean: Return True if the cache is expired.
        """
        if self.name is None or ClientCache.cache_list.peek(self.name).is_expired():
            return True
        return False
    
    def get_cache(self):
        """
        Get cache node and return its stored value.
    
        Returns:
            data (Object): Cache stored by the provided key. None if the provided key does not exist in cache or has been expired.
        """
        logger.trace(str(self))
        cache_node = ClientCache.cache_list.pop(self.name)
        if cache_node and not cache_node.is_expired():
            data = cache_node.get_value()
            ClientCache.cache_list.add_to_head(key=None, data=cache_node)
            logger.debug(f"Data {self.name} retrieved from cache.")
        else:
            data = None
            logger.debug(f"Data {self.name} from cache is either not exist or expired.")
        return data
    
    def set_cache(self, data):
        """
        Generic set cache data.
    
        Parameters:
            data (Object): Data to load manually.

        Returns:
            data (Object): Data to load manually.
        """
        if ClientCache.cache_list.loc(self.name) >= 0:
            cache_node = ClientCache.cache_list.pop(self.name)
            logger.debug(f"Cache {self.name} removed before set_cache.")
            cache_node.set_value(data)
            ClientCache.cache_list.add_to_head(key=None, data=cache_node)
        else:
            ClientCache.cache_list.add_to_head(self.name, data)            
        logger.debug(f"Cache {self.name} configured from set_cache.")
        return data
    
    def clear_cache(self):
        """
        Generic clear cache to force the cache to retrieve the latest content in later get cache runs.

        Returns:
            data (any Object): Data of the cleared cache.
        """
        data = ClientCache.cache_list.pop(self.name).get_value()
        logger.debug(f"Cache {self.name} cleared.")
        return data

class ClientDropdownCache(ClientCache):
    def __init__(self, funcname):
        """
        Client dropdown cache initialization.

        Parameters:
            key (string): A key for client dropdown cache object.
        """
        super().__init__(funcname)

    def get_cache(self):
        """
        Get cache node, return and format its stored value into a dropdown list format defined in the client constants module per client cache's name.
    
        Returns:
            result (list of list): Drop down list items transformed per lambda function defined in client constants module by client cache's name.
        """
        result = None
        mapping = CacheDropdown.DROPDOWN_MAPPPING.get(self.name, None)
        if mapping:
            func, transform = mapping
            if self.is_empty() or self.is_expired():
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
        data = self.get_cache()
        if data is not None:
            if partial_key and any(isinstance(i, (list, tuple)) for i in data):
                return next((item[1] for item in data if partial_key in item[1]), partial_key)
            else:
                return partial_key
        return partial_key

class ClientPersistentCache(ClientCache):
    def __init__(self, funcname):
        """
        Client persistent cache initialization.

        Parameters:
            key (string): A key for client persistent cache object.
        """
        from ..Entities.CacheListNode import Node
        super().__init__(funcname)
        position = ClientCache.cache_list.loc(self.name)
        if position < 0:
            ClientCache.cache_list.add_to_head(key=None, data=Node(self.name, [], minutes=0))

    def is_expired(self):
        """
        Check if the cache is expired.

        As this class is persistent cache, it means cache node never expires, hence always return False.
    
        Returns:
            boolean: Return False all the time as persistent nature.
        """
        return False
    
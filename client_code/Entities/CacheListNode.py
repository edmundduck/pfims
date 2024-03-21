import anvil.server
from datetime import datetime, timedelta
from ..Utils.Constants import CacheExpiry

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

class Node:
    def __init__(self, key, data, minutes=None):
        """
        Cache node object initialization.

        Node for double linked list with expiry time.
    
        Parameters:
            key (string): The key of the cache node for lookup.
            data (Object): Data to stored in cache.
            minutes (int): Optional. If present, define the customized minute for the cache to expire, otherwise pre-define the value from Client Constants module. If equal to 0, then become non-expired cache, i.e. expiry = None.
        """
        self.key = key
        self.data = data
        self.prev = None
        self.next = None
        self.duration = minutes if minutes is not None else CacheExpiry.MINUTES
        self.expirytime = datetime.now() + timedelta(minutes=self.duration) if self.duration != 0 else None

    def __str__(self):
        """
        String presentation of the cache node.

        Returns:
            string: The string presentation of the cache node for logger print out.
        """
        return "[{0}: {1} {2} {3} {4} {5}]".format(
            self.__class__,
            self.key,
            self.data,
            self.prev,
            self.next,
            self.expirytime
        )

    def get_next(self):
        """
        Get the next linked cache node.

        Returns:
            self.next (Node): Next linked cache node.
        """
        return self.next

    def get_prev(self):
        """
        Get the previous linked cache node.

        Returns:
            self.prev (Node): Previous linked cache node.
        """
        return self.prev

    def get_key(self):
        """
        Get the key of the cache node.

        Returns:
            self.key (string): The key of the cache node.
        """
        return self.key
    
    def get_value(self):
        """
        Get the value of the cache node.

        Expiry time is refreshed upon the access of cache node value.

        Returns:
            self.data (Object): The stored value of the cache node.
        """
        if self.duration != 0:
            self.expirytime = datetime.now() + timedelta(minutes=self.duration)
        return self.data

    def get_expiry(self):
        """
        Get the expiry time of the cache node.

        Returns:
            self.expirytime (datetime): The expiry time of the cache node.
        """
        return self.expirytime

    def is_expired(self):
        """
        Get the expiry status of the cache node.

        Returns:
            boolean: True if cache node is expired, otherwise False.
        """
        return True if self.duration != 0 and datetime.now() > self.expirytime else False

    def set_next(self, node):
        """
        Set the next linked cache node.

        Parameters:
            node (Node): The cache node to link next to the current cache node.
        """
        self.next = node

    def set_prev(self, node):
        """
        Set the previous linked cache node.

        Parameters:
            node (Node): The cache node to link previous to the current cache node.
        """
        self.prev = node

    def set_key(self, data):
        """
        Set the key of the linked cache node.

        Parameters:
            data (string): The key of the cache node.
        """
        self.key = data

    def set_value(self, data):
        """
        Set the value of the linked cache node.

        Expiry time is refreshed upon the access of cache node value.

        Parameters:
            data (string): The value to stored into the cache node.
        """
        self.data = data
        if self.duration != 0:
            self.expirytime = datetime.now() + timedelta(minutes=self.duration)

class DoubleLinkedList:
    def __init__(self):
        """
        Double linked list object initialization.

        List is composed of cache node.
        """
        self.head = None
        self.tail = None

    def __str__(self):
        """
        String presentation of the double linked list.

        Returns:
            string: The string presentation of the double linked list for logger print out.
        """
        whole_list = []
        current_node = self.head
        while current_node:
            whole_list.append(f"[{','.join((current_node.get_key(), str(current_node.get_expiry()), str(current_node.is_expired())))}] ")
            current_node = current_node.get_next()
        return "Cache {0} structure - {1}".format(
            self.__class__,
            str(whole_list)
        )

    def add_to_head(self, key, data):
        """
        Add data to the head of the double linked list.
        
        Cache node will be created in the process.

        Parameters:
            key (string): The key of the cache node for lookup.
            data (Object): Data to stored in cache.
        """
        if isinstance(data, Node):
            new_node = data
        else:
            if key:
                new_node = Node(key, data)
            else:
                raise TypeError('Key cannot be None or blank if data is not a Node.')
        if self.head:
            new_node.set_next(self.head)
            self.head.set_prev(new_node)
            self.head = new_node
        else:
            self.head = new_node
            self.tail = new_node
            new_node.set_prev(None)

    def add_to_tail(self, key, data):
        """
        Add data to the tail of the double linked list.
        
        Cache node will be created in the process.

        Parameters:
            key (string): The key of the cache node for lookup.
            data (Object): Data to stored in cache.
        """
        if isinstance(data, Node):
            new_node = data
        else:
            if key:
                new_node = Node(key, data)
            else:
                raise TypeError('Key cannot be None or blank if data is not a Node.')
        if self.tail:
            new_node.set_prev(self.tail)
            self.tail.set_next(new_node)
            self.tail = new_node
        else:
            self.head = new_node
            self.tail = new_node
            new_node.set_next(None)

    def remove_from_head(self):
        """
        Remove the head from the double linked list.

        The cache node is returned instead of the data stored inside the cache node.
        
        Returns:
            unwanted_node (Node): The removed cache node from the head.
        """
        unwanted_node = self.head
        if unwanted_node:
            self.head = unwanted_node.get_next()
            unwanted_node.next = None
        if self.head:
            self.head.prev = None
        return unwanted_node

    def remove_from_tail(self):
        """
        Remove the tail from the double linked list.

        The cache node is returned instead of the data stored inside the cache node.
        
        Returns:
            unwanted_node (Node): The removed cache node from the tail.
        """
        unwanted_node = self.tail
        if unwanted_node:
            self.tail = unwanted_node.get_prev()
            unwanted_node.prev = None
        if self.tail:
            self.tail.next = None
        return unwanted_node

    def pop(self, key):
        """
        Pop the requested cache node per key from the double linked list.

        Returns:
            node_to_search (Node): The popped (removed) cache node from the double linked list. If no node is found per the key, a node with empty value is returned.
        """
        node_to_search = self.head
        position = self.loc(key)
        if position > -1:
            for i in range(position):
                node_to_search = node_to_search.get_next()
            if not node_to_search.get_prev():
                return self.remove_from_head()
            elif not node_to_search.get_next():
                return self.remove_from_tail()
            else:
                prev_node = node_to_search.get_prev()
                next_node = node_to_search.get_next()
                prev_node.set_next(next_node)
                next_node.set_prev(prev_node)
                node_to_search.set_prev(None)
                node_to_search.set_next(None)
                return node_to_search
        else:
            return Node(key, None)

    def peek(self, key):
        """
        Peek the requested cache node per key in the double linked list without popping out.

        Returns:
            node_to_search (Node): The requested cache node from the double linked list. If no node is found per the key, a node with empty value is returned.
        """
        node_to_search = self.head
        position = self.loc(key)
        if position > -1:
            for i in range(position):
                node_to_search = node_to_search.get_next()
            return node_to_search
        else:
            return Node(key, None)

    def loc(self, key):
        """
        Get the location of the requested cache node per key in the double linked list.

        Returns:
            position (int): The location of the requested cache node per key. If no node is found per the key, return -1.
        """
        node_to_search = self.head
        position = 0
        while node_to_search:
            if node_to_search.get_key() == key:
                return position
            else:
                node_to_search = node_to_search.get_next()
                position += 1
        return -1
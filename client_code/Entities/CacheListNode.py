import anvil.server
from datetime import datetime, timedelta
from ..Utils.Constants import CacheExpiry

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

class Node:
    def __init__(self, key, data, minutes=None):
        self.key = key
        self.data = data
        self.prev = None
        self.next = None
        self.duration = minutes if minutes else CacheExpiry.MINUTES
        self.expirytime = datetime.now() + timedelta(minutes=self.duration)

    def __str__(self):
        return "CacheNode {0}: [{1} {2} {3} {4} {5}]".format(
            self.__class__,
            self.key,
            self.data,
            self.prev,
            self.next,
            self.expirytime
        )

    def get_next(self):
        return self.next

    def get_prev(self):
        return self.prev

    def get_key(self):
        return self.key
    
    def get_value(self):
        self.expirytime = datetime.now() + timedelta(minutes=self.duration)
        return self.data

    def is_expired(self):
        return True if datetime.now() > self.expirytime else False

    def set_next(self, data):
        self.next = data

    def set_prev(self, data):
        self.prev = data

    def set_key(self, data):
        self.key = data

    def set_value(self, data):
        self.data = data
        self.expirytime = datetime.now() + timedelta(minutes=self.duration)

class DoubleLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None

    def __str__(self):
        whole_list = []
        current_node = self.head
        while current_node:
            whole_list.append(f"[{','.join((current_node.get_key(), str(current_node.is_expired())))}] ")
            current_node = current_node.get_next()
        return "Cache {0} structure -\n{1}".format(
            self.__class__,
            str(whole_list)
        )

    def add_to_head(self, key, data):
        new_node = Node(key, data)
        if self.head:
            new_node.set_next(self.head)
            self.head.set_prev(new_node)
            self.head = new_node
        else:
            self.head = new_node
            self.tail = new_node
            new_node.set_prev(None)

    def add_to_tail(self, key, data):
        new_node = Node(key, data)
        if self.tail:
            new_node.set_prev(self.tail)
            self.tail.set_next(new_node)
            self.tail = new_node
        else:
            self.head = new_node
            self.tail = new_node
            new_node.set_next(None)

    def remove_from_head(self):
        unwanted_node = self.head
        if unwanted_node:
            self.head = unwanted_node.get_next()
            unwanted_node.next = None
        if self.head:
            self.head.prev = None
        return unwanted_node.get_value()

    def remove_from_tail(self):
        unwanted_node = self.tail
        if unwanted_node:
            self.tail = unwanted_node.get_prev()
            unwanted_node.prev = None
        if self.tail:
            self.tail.next = None
        return unwanted_node.get_value()

    def pop(self, data):
        node_to_search = self.head
        # while node_to_search:
        #     if node_to_search.get_key() == data:
        #         if not node_to_search.get_prev():
        #             return self.remove_from_head()
        #         elif not node_to_search.get_next():
        #             return self.remove_from_tail()
        #         else:
        #             prev_node = node_to_search.get_prev()
        #             next_node = node_to_search.get_next()
        #             prev_node.set_next(next_node)
        #             next_node.set_prev(prev_node)
        #             node_to_search.set_prev(None)
        #             node_to_search.set_next(None)
        #             return node_to_search.get_value()
        #     else:
        #         node_to_search = node_to_search.get_next()
        position = self.loc(data)
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
                return node_to_search.get_value()
            return node_to_search.get_value()
        else:
            return None

    def loc(self, data):
        node_to_search = self.head
        position = 0
        while node_to_search:
            if node_to_search.get_key() == data:
                return position
            else:
                node_to_search = node_to_search.get_next()
                position += 1
        return -1
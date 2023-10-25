import anvil.server

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

class Node:
    def __init__(self, data):
        self.data = data
        self.prev = None
        self.next = None

    def get_next(self):
        return self.next

    def get_prev(self):
        return self.prev

    def get_value(self):
        return self.data

    def set_next(self, data):
        self.next = Node(data)

    def set_prev(self, data):
        self.prev = Node(data)

    def set_value(self, data):
        self.data = data

class DoubleLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None

    def add_to_head(self, data):
        new_node = Node(data)
        if self.head:
            new_node.set_next(self.head)
            self.head.set_prev(new_node)
            self.head = new_node
        else:
            self.head = new_node
            self.tail = new_node
            new_node.set_prev(None)

    def add_to_tail(self, data):
        new_node = Node(data)
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
        node_to_search = this.head
        while node_to_search:
            if node_to_search.get_value() == data:
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
            else:
                node_to_search = node_to_search.get_next()
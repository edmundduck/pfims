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

    def set_next(self, data):
        self.next = Node(data)

    def set_prev(self, data):
        self.prev = Node(data)

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
        

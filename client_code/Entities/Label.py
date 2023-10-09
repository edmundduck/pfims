import anvil.server
import anvil.users
# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

class Label:
    def __init__(self, data):
        self.set(data)

    def get(self):
        return [self.id, self.name, self.status, self.keywords]
        
    def set(self, data):
        if data and isinstance(data, list):
            self.id = data[0]
            self.name = data[1]
            self.status = data[2]
            self.keywords = data[3]

    def is_valid(self):
        if not self.name or self.name.isspace(): return False
        return True
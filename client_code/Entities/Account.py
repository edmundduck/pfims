import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

class Account:
    def __init__(self, data):
        self.set(data)

    def get(self):
        return [self.id, self.name, self.ccy, self.valid_from, self.valid_to, self.status]
        
    def set(self, data):
        if data and isinstance(data, list):
            self.id = data[0]
            self.name = data[1]
            self.ccy = data[2]
            self.valid_from = data[3]
            self.valid_to = data[4]
            self.status = data[5]

    def is_valid(self):
        if not self.name or self.name.isspace():
            return False
        if not self.ccy or self.ccy.isspace():
            return False
        return True
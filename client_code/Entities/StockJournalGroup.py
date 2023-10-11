import anvil.server
import anvil.users
# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

class StockJournalGroup:
    def __init__(self, data):
        self.set(data)

    def get(self):
        return [self.id, self.name, self.broker_id, self.submitted, self.created_time, self.lastsaved_time, self.submitted_time, self.journals]
        
    def set(self, data):
        if data and isinstance(data, list):
            self.id = data[0]
            self.name = data[1]
            self.broker_id = data[2]
            self.submitted = data[3]
            self.created_time = data[4]
            self.lastsaved_time = data[5]
            self.submitted_time = data[6]
            self.journals = data[7]

    def is_valid(self):
        if not self.name or self.name.isspace(): return False
        if not self.broker_id or self.broker_id.isspace(): return False
        return True
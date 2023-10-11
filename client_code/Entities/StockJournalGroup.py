import anvil.server
import anvil.users
# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

class StockJournalGroup:
    __column_def__ = ['userid', 'template_id', 'template_name', 'broker_id', 'submitted', 'template_create', 'template_lastsave', 'template_submitted', 'journals']
    
    def __init__(self, data):
        self.set(data)

    def __str__(self):
        return "{0}: {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}".format(
            self.__class__,
            self.id, 
            self.name, 
            self.broker_id, 
            self.submitted, 
            self.create_time,
            self.lastsave_time,
            self.submit_time,
            len(self.journals)
        )

    def get_dict(self):
        return {
            self.__column_def__[0]: self.userid,
            self.__column_def__[1]: self.id,
            self.__column_def__[2]: self.name,
            self.__column_def__[3]: self.broker_id,
            self.__column_def__[4]: self.submitted,
            self.__column_def__[5]: self.create_time,
            self.__column_def__[6]: self.lastsave_time,
            self.__column_def__[7]: self.submit_time,
            self.__column_def__[8]: self.journals
        }

    def get_list(self):
        return [
            self.userid,
            self.id,
            self.name,
            self.broker_id,
            self.submitted,
            self.create_time,
            self.lastsave_time,
            self.submit_time,
            self.journals
        ]

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name
    
    def get_broker(self):
        return self.broker_id

    def get_submitted_status(self):
        return self.submitted

    def get_created_time(self):
        return self.create_time

    def get_lastsaved_time(self):
        return self.lastsave_time

    def get_submitted_time(self):
        return self.submit_time

    def get_journals(self):
        return self.journals

    def set(self, data):
        if data:
            if isinstance(data, dict):
                self.userid = data.get('userid')
                self.id = data.get('template_id')
                self.name = data.get('template_name')
                self.broker_id = data.get('broker_id')
                self.submitted = data.get('submitted')
                self.create_time = data.get('template_create')
                self.lastsave_time = data.get('template_lastsave')
                self.submit_time = data.get('template_submitted')
                self.journals = data.get('journals')
            elif isinstance(data, (list, tuple)):
                self.userid = data[0]
                self.id = data[1]
                self.name = data[2]
                self.broker_id = data[3]
                self.submitted = data[4]
                self.create_time = data[5]
                self.lastsave_time = data[6]
                self.submit_time = data[7]
                self.journals = data[8]

    def is_valid(self):
        if not self.name or self.name.isspace(): return False
        if not self.broker_id or self.broker_id.isspace(): return False
        return True

    def __serialize__(self, global_data):
        global_data[f"StockJournalGroup_{self.userid}"] = self.get_dict()
        return self.userid

    def __deserialize__(self, userid, global_data):
        data = global_data[f"StockJournalGroup_{userid}"]
        self.__init__(data)

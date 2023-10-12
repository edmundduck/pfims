import anvil.server
import anvil.users
# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

@anvil.server.portable_class
class StockJournalGroup:
    __db_column_def__ = ['userid', 'template_id', 'template_name', 'broker_id', 'submitted', 'template_create', 'template_lastsave', 'template_submitted']
    __property_def__ = __db_column_def__ + ['journals']
    
    def __init__(self, data=None):
        if data:
            self.set(data)
        else:
            self.set([None]*9)

    def __str__(self):
        return '{0}: {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}'.format(
            self.__class__,
            self.userid, 
            self.id, 
            self.name, 
            self.broker_id, 
            self.submitted, 
            self.create_time,
            self.lastsave_time,
            self.submit_time,
            self.journals
        )

    @staticmethod
    def get_column_definition():
        return ', '.join(c for c in StockJournalGroup.__db_column_def__)

    def get_dict(self):
        for i in range(len(self.__property_def__)):
            print(eval(''.join(('self.', self.__property_def__[i]))))
        return {
            # self.__property_def__[0]: self.userid,
            # self.__property_def__[1]: self.id,
            # self.__property_def__[2]: self.name,
            # self.__property_def__[3]: self.broker_id,
            # self.__property_def__[4]: self.submitted,
            # self.__property_def__[5]: self.create_time,
            # self.__property_def__[6]: self.lastsave_time,
            # self.__property_def__[7]: self.submit_time,
            # self.__property_def__[8]: self.journals
            self.__property_def__[i]: eval(''.join(('a.', self.__property_def__[i]))) for i in range(len(self.__property_def__))
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

    def set_broker(self, broker_id):
        copy = self.copy()
        copy.broker_id = broker_id
        return copy
        
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

    def set_journals(self, journals):
        copy = self.copy()
        copy.journals = journals
        return copy
        
    def set(self, data):
        if data:
            if isinstance(data, dict):
                self.userid = data.get('userid', None)
                self.id = data.get('template_id', None)
                self.name = data.get('template_name', None)
                self.broker_id = data.get('broker_id', None)
                self.submitted = data.get('submitted', None)
                self.create_time = data.get('template_create', None)
                self.lastsave_time = data.get('template_lastsave', None)
                self.submit_time = data.get('template_submitted', None)
                self.journals = data.get('journals', None)
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

    def copy(self):
        print("PRINT!!", self.get_dict())
        return StockJournalGroup(self.get_dict())

    def is_valid(self):
        if not self.name or self.name.isspace(): return False
        if not self.broker_id or self.broker_id.isspace(): return False
        return True

    def __serialize__(self, global_data):
        global_data[f"{__class__.__name__}_{self.userid}"] = self.get_dict()
        return self.userid

    def __deserialize__(self, userid, global_data):
        data = global_data[f"{__class__.__name__}_{userid}"]
        self.__init__(data)

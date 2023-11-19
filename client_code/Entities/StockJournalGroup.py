import anvil.server
from .BaseEntity import BaseEntity
from .StockJournal import StockJournal

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

@anvil.server.portable_class
class StockJournalGroup(BaseEntity):
    __db_column_def__ = ['userid', 'template_id', 'template_name', 'broker_id', 'submitted', 'template_create', 'template_lastsave', 'template_submitted']
    __property_def__ = __db_column_def__ + ['journals']
    
    def __init__(self, data=None):
        super().__init__(data)

    @staticmethod
    def get_column_definition():
        return ', '.join(c for c in StockJournalGroup.__db_column_def__)

    def get_user_id(self):
        return getattr(self, self.__property_def__[0], None)
        
    def get_id(self):
        return getattr(self, self.__property_def__[1], None)

    def get_name(self):
        return getattr(self, self.__property_def__[2], None)
    
    def get_broker(self):
        return getattr(self, self.__property_def__[3], None)

    def get_submitted_status(self):
        return getattr(self, self.__property_def__[4], None)

    def get_created_time(self):
        return getattr(self, self.__property_def__[5], None)

    def get_lastsaved_time(self):
        return getattr(self, self.__property_def__[6], None)

    def get_submitted_time(self):
        return getattr(self, self.__property_def__[7], None)

    def get_journals(self):
        return getattr(self, self.__property_def__[8], [])

    def set_user_id(self, userid):
        return self.set_single_attribute(0, userid)

    def set_id(self, id):
        return self.set_single_attribute(1, id)
        
    def set_name(self, name):
        return self.set_single_attribute(2, name)
        
    def set_broker(self, broker_id):
        return self.set_single_attribute(3, broker_id)
        
    def set_submitted_status(self, status):
        return self.set_single_attribute(4, status)
        
    def set_created_time(self, created_time):
        return self.set_single_attribute(5, created_time)
        
    def set_lastsaved_time(self, lastsaved_time):
        return self.set_single_attribute(6, lastsaved_time)
        
    def set_submitted_time(self, submitted_time):
        return self.set_single_attribute(7, submitted_time)
        
    def set_journals(self, journals):
        if isinstance(journals, StockJournal):
            return self.set_single_attribute(8, [journals.set_group_id(self.get_id())])
        elif isinstance(journals, list):
            journal_list = []
            for j in journals:
                if isinstance(j, StockJournal):
                    journal_list.append(j.set_group_id(self.get_id()))
                elif isinstance(j, dict):
                    journal_list.append(StockJournal(j).set_group_id(self.get_id()))
            return self.set_single_attribute(8, journal_list)

    def copy(self):
        return StockJournalGroup(self.get_dict())

    def is_valid(self):
        from ..Error.ValidationError import ValidationError
        
        group_name, broker_id, journals = [self.get_name(), self.get_broker(), self.get_journals()]
        err_msg = ""
        if not group_name or group_name.isspace(): err_msg = err_msg + '- Group name cannot be empty\n'
        if not broker_id or broker_id.isspace(): err_msg = err_msg + '- Broker cannot be empty\n'
        for j in journals:
            if not j.is_valid():
                err_msg = err_msg + str(j.get_exception()) + '\n'
        if not err_msg:
            return True
        else:
            self.set_exception(ValidationError(err_msg))
            return False

import anvil.server
import anvil.users
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

    def get_id(self):
        return getattr(self, self.__property_def__[1], None)

    def get_name(self):
        return getattr(self, self.__property_def__[2], None)
    
    def set_name(self, name):
        copy = self.copy()
        copy.name = name
        return copy
        
    def get_broker(self):
        return getattr(self, self.__property_def__[3], None)

    def set_broker(self, broker_id):
        copy = self.copy()
        copy.broker_id = broker_id
        return copy
        
    def get_submitted_status(self):
        return getattr(self, self.__property_def__[4], None)

    def get_created_time(self):
        return getattr(self, self.__property_def__[5], None)

    def get_lastsaved_time(self):
        return getattr(self, self.__property_def__[6], None)

    def get_submitted_time(self):
        return getattr(self, self.__property_def__[7], None)

    def get_journals(self):
        return getattr(self, self.__property_def__[8], None)

    def set_journals(self, journals):
        copy = self.copy()
        if isinstance(journals, StockJournal):
            copy.journals = StockJournal(journals)
        elif isinstance(journals, list):
            copy.journals = list(StockJournal(j) for j in journals)
        return copy

    def copy(self):
        return StockJournalGroup(self.get_dict())

    def is_valid(self):
        group_name, broker_id = [self.get_name(), self.get_broker()]
        if not group_name or group_name.isspace(): return False
        if not broker_id or broker_id.isspace(): return False
        return True

import anvil.server
import anvil.users
from . import BaseEntity
# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

@anvil.server.portable_class
class StockJournalGroup(BaseEntity):
    __db_column_def__ = ['userid', 'template_id', 'template_name', 'broker_id', 'submitted', 'template_create', 'template_lastsave', 'template_submitted']
    __property_def__ = __db_column_def__ + ['journals']
    
    def __init__(self, data=None):
        super().__init__(data)

    # @staticmethod
    # def get_column_definition():
    #     return ', '.join(c for c in StockJournalGroup.__db_column_def__)

    def get_id(self):
        return getattr(self, self.__property_def__[1])

    def get_name(self):
        return getattr(self, self.__property_def__[2])
    
    def get_broker(self):
        return getattr(self, self.__property_def__[3])

    def set_broker(self, broker_id):
        copy = self.copy()
        copy.broker_id = broker_id
        return copy
        
    def get_submitted_status(self):
        return getattr(self, self.__property_def__[4])

    def get_created_time(self):
        return getattr(self, self.__property_def__[5])

    def get_lastsaved_time(self):
        return getattr(self, self.__property_def__[6])

    def get_submitted_time(self):
        return getattr(self, self.__property_def__[7])

    def get_journals(self):
        return getattr(self, self.__property_def__[8])

    def set_journals(self, journals):
        copy = self.copy()
        copy.journals = journals
        return copy

    # def copy(self):
    #     return StockJournalGroup(self.get_dict())

    def is_valid(self):
        if not self.template_name or self.template_name.isspace(): return False
        if not self.broker_id or self.broker_id.isspace(): return False
        return True

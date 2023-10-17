import anvil.server
import anvil.users
from .BaseEntity import BaseEntity

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

@anvil.server.portable_class
class Setting(BaseEntity):
    __db_column_def__ = ['userid', 'default_broker', 'default_interval', 'default_datefrom', 'default_dateto', 'logging_level']
    __property_def__ = __db_column_def__
    
    def __init__(self, data=None):
        super().__init__(data)

    @staticmethod
    def get_column_definition():
        return ', '.join(c for c in Setting.__db_column_def__)

    def get_user_id(self):
        return getattr(self, self.__property_def__[0], None)

    def get_broker(self):
        return getattr(self, self.__property_def__[1], None)

    def get_search_interval(self):
        return getattr(self, self.__property_def__[2], None)

    def get_search_datefrom(self):
        return getattr(self, self.__property_def__[3], None)

    def get_search_dateto(self):
        return getattr(self, self.__property_def__[4], None)

    def get_logging_level(self):
        return getattr(self, self.__property_def__[5], None)

    def set_user_id(self, userid):
        return self.set_single_attribute(0, userid)

    def set_broker(self, broker_id):
        return self.set_single_attribute(1, broker_id)

    def set_search_interval(self, interval):
        return self.set_single_attribute(2, interval)

    def set_search_datefrom(self, datefrom):
        return self.set_single_attribute(3, datefrom)

    def set_search_dateto(self, dateto):
        return self.set_single_attribute(4, dateto)

    def set_logging_level(self, level):
        return self.set_single_attribute(5, level)

    def copy(self):
        return Setting(self.get_dict())

    def is_valid(self):
        return True

import anvil.server
from .BaseEntity import BaseEntity

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

@anvil.server.portable_class
class Label(BaseEntity):
    __db_column_def__ = ['userid', 'id', 'name', 'status', 'keywords']
    __property_def__ = __db_column_def__

    def __init__(self, data=None):
        super().__init__(data)

    @staticmethod
    def get_column_definition():
        return ', '.join(c for c in Label.__db_column_def__)

    def get_user_id(self):
        return getattr(self, self.__property_def__[0], None)

    def get_id(self):
        return getattr(self, self.__property_def__[1], None)

    def get_name(self):
        return getattr(self, self.__property_def__[2], None)

    def get_status(self):
        return getattr(self, self.__property_def__[3], None)

    def get_keywords(self):
        return getattr(self, self.__property_def__[4], None)

    def set_user_id(self, userid):
        return self.set_single_attribute(0, userid)

    def set_id(self, id):
        return self.set_single_attribute(1, id)

    def set_name(self, name):
        return self.set_single_attribute(2, name)

    def set_status(self, status):
        return self.set_single_attribute(3, status)

    def set_keywords(self, keywords):
        return self.set_single_attribute(4, keywords)

    def copy(self):
        return Label(self.get_dict())

    def is_valid(self):
        lbl_name, status = [self.get_name(), self.get_status()]
        if not lbl_name or lbl_name.isspace(): return False
        if not status or status.isspace(): return False
        return True
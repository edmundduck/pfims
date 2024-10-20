import anvil.server
from .BaseEntity import BaseEntity

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

@anvil.server.portable_class
class Account(BaseEntity):
    __db_column_def__ = ['userid', 'id', 'name', 'ccy', 'valid_from', 'valid_to', 'status']
    __property_def__ = __db_column_def__
    
    def __init__(self, data=None):
        super().__init__(data)

    @staticmethod
    def get_column_definition():
        return ', '.join(c for c in Account.__db_column_def__)

    @staticmethod
    def field_user_id():
        return Account.__property_def__[0]

    @staticmethod
    def field_id():
        return Account.__property_def__[1]

    @staticmethod
    def field_name():
        return Account.__property_def__[2]

    @staticmethod
    def field_base_currency():
        return Account.__property_def__[3]

    @staticmethod
    def field_valid_datefrom():
        return Account.__property_def__[4]

    @staticmethod
    def field_valid_dateo():
        return Account.__property_def__[5]

    @staticmethod
    def field_status():
        return Account.__property_def__[6]

    def get_user_id(self):
        return getattr(self, self.__property_def__[0], None)

    def get_id(self):
        return getattr(self, self.__property_def__[1], None)

    def get_name(self):
        return getattr(self, self.__property_def__[2], None)

    def get_base_currency(self):
        return getattr(self, self.__property_def__[3], None)

    def get_valid_datefrom(self):
        return getattr(self, self.__property_def__[4], None)

    def get_valid_dateto(self):
        return getattr(self, self.__property_def__[5], None)

    def get_status(self):
        return getattr(self, self.__property_def__[6], None)

    def set_user_id(self, userid):
        return self.set_single_attribute(0, userid)

    def set_id(self, id):
        return self.set_single_attribute(1, id)

    def set_name(self, name):
        return self.set_single_attribute(2, name)

    def set_base_currency(self, ccy):
        return self.set_single_attribute(3, ccy)

    def set_valid_datefrom(self, datefrom):
        return self.set_single_attribute(4, datefrom)

    def set_valid_dateto(self, dateto):
        return self.set_single_attribute(5, dateto)

    def set_status(self, status):
        return self.set_single_attribute(6, status)

    def copy(self):
        return Account(self.get_dict())

    def is_valid(self):
        from ..Error.ValidationError import ValidationError

        acct_name, ccy, status = [self.get_name(), self.get_base_currency(), self.get_status()]
        err_msg = ""
        if not acct_name or acct_name.isspace(): err_msg = err_msg + '- Account name cannot be empty\n'
        if not ccy or ccy.isspace(): err_msg = err_msg + '- Currency cannot be empty\n'
        if not status or status.isspace():  err_msg = err_msg + '- Status cannot be empty\n'
        if not err_msg:
            return True
        else:
            self.set_exception(ValidationError(err_msg))
            return False

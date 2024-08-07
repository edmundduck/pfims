import anvil.server
from datetime import datetime
from .BaseEntity import BaseEntity

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

@anvil.server.portable_class
class ExpenseTransaction(BaseEntity):
    # __db_column_def__ = ['iid', 'tab_id', 'trandate', 'account_id', 'amount', 'labels', 'remarks', 'stmt_dtl']
    __db_column_def__ = ['iid', 'tab_id', 'DTE', 'ACC', 'AMT', 'LBL', 'RMK', 'STD']
    __property_def__ = ['userid'] + __db_column_def__
    __data_transform_def__ = ['DTE', 'ACC', 'AMT', 'LBL', 'RMK', 'STD', 'EXTLBL']
    
    def __init__(self, data=None):
        super().__init__(data)

    @staticmethod
    def get_column_definition():
        return ', '.join(c for c in ExpenseTransaction.__db_column_def__)

    @staticmethod
    def get_data_transform_definition():
        return ExpenseTransaction.__data_transform_def__

    @staticmethod
    def field_date():
        return ExpenseTransaction.__data_transform_def__[0]

    @staticmethod
    def field_account():
        return ExpenseTransaction.__data_transform_def__[1]
    
    @staticmethod
    def field_amount():
        return ExpenseTransaction.__data_transform_def__[2]

    @staticmethod
    def field_labels():
        return ExpenseTransaction.__data_transform_def__[3]

    @staticmethod
    def field_remarks():
        return ExpenseTransaction.__data_transform_def__[4]

    @staticmethod
    def field_statement_detail():
        return ExpenseTransaction.__data_transform_def__[5]

    @staticmethod
    # A column which contains extra labels introduced by upload mapping criteria rules
    def field_extra_labels():
        return ExpenseTransaction.__data_transform_def__[6]

    def get_user_id(self):
        return getattr(self, self.__property_def__[0], None)
        
    def get_item_id(self):
        return getattr(self, self.__property_def__[1], None)

    def get_group_id(self):
        return getattr(self, self.__property_def__[2], None)
        
    def get_tnx_date(self):
        return getattr(self, self.__property_def__[3], None)
    
    def get_account(self):
        return getattr(self, self.__property_def__[4], None)
        
    def get_amount(self):
        return getattr(self, self.__property_def__[5], None)

    def get_labels(self):
        return getattr(self, self.__property_def__[6], None)

    def get_remarks(self):
        return getattr(self, self.__property_def__[7], None)

    def get_statement_detail(self):
        return getattr(self, self.__property_def__[8], None)

    def set_user_id(self, userid):
        return self.set_single_attribute(0, userid)
        
    def set_item_id(self, iid):
        return self.set_single_attribute(1, iid)

    def set_group_id(self, gid):
        return self.set_single_attribute(2, gid)
        
    def set_tnx_date(self, tnx_date):
        return self.set_single_attribute(3, tnx_date)
    
    def set_account(self, account):
        return self.set_single_attribute(4, account)
        
    def set_amount(self, amount):
        return self.set_single_attribute(5, amount)

    def set_labels(self, labels):
        return self.set_single_attribute(6, labels)

    def set_remarks(self, remarks):
        return self.set_single_attribute(7, remarks)

    def set_statement_detail(self, stmt_dtl):
        return self.set_single_attribute(8, stmt_dtl)

    def copy(self):
        return ExpenseTransaction(self.get_dict())

    def is_valid(self):
        from ..Error.ValidationError import ValidationError

        tnx_date, account, amount = [self.get_tnx_date(), self.get_account(), self.get_amount()]
        err_msg = ""
        date_format = '%Y-%m-%d'
        if not tnx_date or str(tnx_date).isspace(): err_msg = err_msg + '- Transaction Date cannot be empty\n'
        # try:
        #     datetime.strptime(tnx_date, date_format)
        # except ValueError as err:
        #     err_msg = err_msg + '- Transaction Date is not in a proper date format\n'
        if not account or str(account).isspace(): err_msg = err_msg + '- Account cannot be empty\n'
        if amount is None or str(amount).isspace(): err_msg = err_msg + '- Amount cannot be empty\n'
        if not err_msg:
            return True
        else:
            self.set_exception(ValidationError(err_msg))
            return False

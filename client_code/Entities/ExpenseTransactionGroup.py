import anvil.server
from .BaseEntity import BaseEntity
from .ExpenseTransaction import ExpenseTransaction

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

@anvil.server.portable_class
class ExpenseTransactionGroup(BaseEntity):
    __db_column_def__ = ['userid', 'tab_id', 'tab_name', 'submitted', 'tab_create', 'tab_lastsave', 'tab_submitted']
    __property_def__ = __db_column_def__ + ['transactions']
    
    def __init__(self, data=None):
        super().__init__(data)

    @staticmethod
    def get_column_definition():
        return ', '.join(c for c in ExpenseTransactionGroup.__db_column_def__)

    def get_user_id(self):
        return getattr(self, self.__property_def__[0], None)
        
    def get_id(self):
        return getattr(self, self.__property_def__[1], None)

    def get_name(self):
        return getattr(self, self.__property_def__[2], None)
    
    def get_submitted_status(self):
        return getattr(self, self.__property_def__[3], None)

    def get_created_time(self):
        return getattr(self, self.__property_def__[4], None)

    def get_lastsaved_time(self):
        return getattr(self, self.__property_def__[5], None)

    def get_submitted_time(self):
        return getattr(self, self.__property_def__[6], None)

    def get_transactions(self):
        return getattr(self, self.__property_def__[7], [])

    def set_user_id(self, userid):
        return self.set_single_attribute(0, userid)

    def set_id(self, id):
        tnx = self.get_transactions()
        if tnx and len(tnx) > 0:
            for t in range(len(tnx)):
                tnx[t] = tnx[t].set_group_id(id)
        return self.set_single_attribute(1, id)
        
    def set_name(self, name):
        return self.set_single_attribute(2, name)
        
    def set_submitted_status(self, status):
        return self.set_single_attribute(3, status)
        
    def set_created_time(self, created_time):
        return self.set_single_attribute(4, created_time)
        
    def set_lastsaved_time(self, lastsaved_time):
        return self.set_single_attribute(5, lastsaved_time)
        
    def set_submitted_time(self, submitted_time):
        return self.set_single_attribute(6, submitted_time)
        
    def set_transactions(self, transactions):
        if isinstance(transactions, ExpenseTransaction):
            return self.set_single_attribute(7, [transactions.set_group_id(self.get_id())])
        elif isinstance(transactions, list):
            transactions_list = []
            for t in transactions:
                if isinstance(t, ExpenseTransaction):
                    transactions_list.append(t.set_group_id(self.get_id()))
                elif isinstance(t, dict):
                    transactions_list.append(ExpenseTransaction(t).set_group_id(self.get_id()))
            return self.set_single_attribute(7, transactions_list)

    def copy(self):
        return ExpenseTransactionGroup(self.get_dict())

    def is_valid(self):
        name, status = [self.get_name(), self.get_submitted_status()]
        if not name or name.isspace(): return False
        if not status or status.isspace(): return False
        return True

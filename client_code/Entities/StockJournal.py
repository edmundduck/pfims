import anvil.server
import anvil.users
import datetime as datetime
# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

@anvil.server.portable_class
class StockJournal:
    __db_column_def__ = ['iid', 'template_id', 'sell_date', 'buy_date', 'symbol', 'qty', 'sales', 'cost', 'fee', 'sell_price', 'buy_price', 'pnl']
    __property_def__ = ['userid'] + __db_column_def__
    
    def __init__(self, data=None):
        if data:
            self.set(data)
        else:
            self.set([None]*13)

    def __str__(self):
        return '{0}: {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}, {10}, {11}, {12}, {13}'.format(
            self.__class__.__name__,
            self.userid, 
            self.iid, 
            self.template_id, 
            self.sell_date, 
            self.buy_date, 
            self.symbol, 
            self.sales,
            self.cost,
            self.fee,
            self.sell_price,
            self.buy_date,
            self.pnl
        )

    @staticmethod
    def get_column_definition():
        return ', '.join(c for c in StockJournal.__db_column_def__)

    def get_dict(self):
        return { self.__property_def__[i]: getattr(self, self.__property_def__[i]) for i in range(len(self.__property_def__)) }

    def get_list(self):
        return [ getattr(self, self.__property_def__[i]) for i in range(len(self.__property_def__)) ]

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
                for i in range(len(self.__property_def__)):
                    setattr(self, self.__property_def__[i], data.get(self.__property_def__[i], None))
            elif isinstance(data, (list, tuple)):
                for i in range(len(self.__property_def__)):
                    setattr(self, self.__property_def__[i], data[i])

    def copy(self):
        return StockJournal(self.get_dict())

    def is_valid(self):
        date_format = '%Y-%m-%d'
        if not self.buy_date or self.buy_date.isspace(): return False
        try:
            datetime.strptime(self.buy_date, date_format)
        except ValueError as err:
            return False
        if not self.symbol or self.symbol.isspace(): return False
        if not self.qty or self.qty.isspace(): return False
        if not self.cost or self.cost.isspace(): return False
        return True

    def __serialize__(self, global_data):
        global_data[f"{__class__.__name}_{self.userid}"] = self.get_dict()
        return self.userid

    def __deserialize__(self, userid, global_data):
        data = global_data[f"{__class__.__name}_{userid}"]
        self.__init__(data)
    
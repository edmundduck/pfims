import anvil.server
import anvil.users
import datetime as datetime
# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

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
            self.__class__,
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
        return ', '.join(c for c StockJournal.__db_column_def__)

    def get_dict(self):
        return {
            self.__property_def__[0]: self.userid,
            self.__property_def__[1]: self.iid,
            self.__property_def__[2]: self.template_id,
            self.__property_def__[3]: self.sell_date,
            self.__property_def__[4]: self.buy_date,
            self.__property_def__[5]: self.symbol,
            self.__property_def__[6]: self.sales,
            self.__property_def__[7]: self.cost,
            self.__property_def__[8]: self.fee,
            self.__property_def__[9]: self.sell_price,
            self.__property_def__[10]: self.buy_date,
            self.__property_def__[11]: self.pnl
        }

    def get_list(self):
        return [
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
                self.iid = data[1]
                self.template_id = data[2]
                self.sell_date = data[3]
                self.buy_date = data[4]
                self.symbol = data[5]
                self.qty = data[6]
                self.sales = data[7]
                self.cost = data[8]
                self.fee = data[9]
                self.sell_price = data[10]
                self.buy_price = data[11]
                self.pnl = data[12]

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

    
    def get(self):
        return [self.id, self.name, self.ccy, self.valid_from, self.valid_to, self.status]
        
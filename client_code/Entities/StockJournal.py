import anvil.server
import anvil.users
import datetime as datetime
from .BaseEntity import BaseEntity
# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

@anvil.server.portable_class
class StockJournal(BaseEntity):
    __db_column_def__ = ['iid', 'template_id', 'sell_date', 'buy_date', 'symbol', 'qty', 'sales', 'cost', 'fee', 'sell_price', 'buy_price', 'pnl']
    __property_def__ = ['userid'] + __db_column_def__
    
    def __init__(self, data=None):
        super().__init__(data)

    @staticmethod
    def get_column_definition():
        return ', '.join(c for c in StockJournal.__db_column_def__)

    def get_item_id(self):
        return getattr(self, self.__property_def__[1], None)

    def get_group_id(self):
        return getattr(self, self.__property_def__[2], None)
        
    def get_sell_date(self):
        return getattr(self, self.__property_def__[3], None)
    
    def get_buy_date(self):
        return getattr(self, self.__property_def__[4], None)
        
    def get_symbol(self):
        return getattr(self, self.__property_def__[5], None)

    def get_number_of_shares(self):
        return getattr(self, self.__property_def__[6], None)

    def get_total_sales(self):
        return getattr(self, self.__property_def__[7], None)

    def get_total_cost(self):
        return getattr(self, self.__property_def__[8], None)

    def get_fee(self):
        return getattr(self, self.__property_def__[9], None)

    def get_unit_price_sold(self):
        return getattr(self, self.__property_def__[10], None)

    def get_unit_price_bought(self):
        return getattr(self, self.__property_def__[11], None)

    def get_profit_n_loss(self):
        return getattr(self, self.__property_def__[12], None)

    def copy(self):
        return StockJournal(self.get_dict())

    def is_valid(self):
        buy_date, symbol, shares, total_cost = [self.get_buy_date(), self.get_symbol(), self.get_number_of_shares(), self.get_total_cost()]
        date_format = '%Y-%m-%d'
        if not buy_date or buy_date.isspace(): return False
        try:
            datetime.strptime(buy_date, date_format)
        except ValueError as err:
            return False
        if not symbol or symbol.isspace(): return False
        if not shares or shares.isspace(): return False
        if not total_cost or total_cost.isspace(): return False
        return True

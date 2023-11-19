import anvil.server
from datetime import datetime
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

    @staticmethod
    def field_item_id():
        return StockJournal.__property_def__[1]
    
    @staticmethod
    def field_group_id():
        return StockJournal.__property_def__[2]

    @staticmethod
    def field_sell_date():
        return StockJournal.__property_def__[3]

    @staticmethod
    def field_buy_date():
        return StockJournal.__property_def__[4]

    @staticmethod
    def field_symbol():
        return StockJournal.__property_def__[5]

    @staticmethod
    def field_quantity():
        return StockJournal.__property_def__[6]

    @staticmethod
    def field_total_sold():
        return StockJournal.__property_def__[7]

    @staticmethod
    def field_total_cost():
        return StockJournal.__property_def__[8]

    @staticmethod
    def field_fee():
        return StockJournal.__property_def__[9]

    @staticmethod
    def field_sold_price():
        return StockJournal.__property_def__[10]

    @staticmethod
    def field_purchased_price():
        return StockJournal.__property_def__[11]

    @staticmethod
    def field_pnl():
        return StockJournal.__property_def__[12]

    def get_user_id(self):
        return getattr(self, self.__property_def__[0], None)
        
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

    def set_user_id(self, userid):
        return self.set_single_attribute(0, userid)
        
    def set_item_id(self, iid):
        return self.set_single_attribute(1, iid)

    def set_group_id(self, gid):
        return self.set_single_attribute(2, gid)
        
    def set_sell_date(self, sell_date):
        return self.set_single_attribute(3, sell_date)
    
    def set_buy_date(self, buy_date):
        return self.set_single_attribute(4, buy_date)
        
    def set_symbol(self, symbol):
        return self.set_single_attribute(5, symbol)

    def set_number_of_shares(self, shares):
        return self.set_single_attribute(6, shares)

    def set_total_sales(self, sales):
        return self.set_single_attribute(7, sales)

    def set_total_cost(self, cost):
        return self.set_single_attribute(8, cost)

    def set_fee(self, fee):
        return self.set_single_attribute(9, fee)

    def set_unit_price_sold(self, price_sold):
        return self.set_single_attribute(10, price_sold)

    def set_unit_price_bought(self, price_bought):
        return self.set_single_attribute(11, price_bought)

    def set_profit_n_loss(self, pnl):
        return self.set_single_attribute(12, pnl)

    def copy(self):
        return StockJournal(self.get_dict())

    def is_valid(self):
        from ..Error.ValidationError import ValidationError

        buy_date, symbol, shares, total_cost = [self.get_buy_date(), self.get_symbol(), self.get_number_of_shares(), self.get_total_cost()]
        err_msg = ""
        date_format = '%Y-%m-%d'
        if not buy_date or str(buy_date).isspace(): err_msg = err_msg + '- Buy Date cannot be empty\n'
        try:
            datetime.strptime(buy_date, date_format)
        except ValueError as err:
            err_msg = err_msg + '- Buy Date is not in a proper date format\n'
        if not symbol or str(symbol).isspace(): err_msg = err_msg + '- Symbol cannot be empty\n'
        if len(symbol) > 8 : err_msg = err_msg + '- Symbol cannot exceed 8 characeters\n'
        if not shares or str(shares).isspace(): err_msg = err_msg + '- Number of shares cannot be empty\n'
        if not total_cost or str(total_cost).isspace(): err_msg = err_msg + '- Total cost cannot be empty\n'
        if not err_msg:
            return True
        else:
            self.set_exception(ValidationError(err_msg))
            return False

    """
    COMMENT OUT customized serialization logic since nesting StockJournal objects inside StockJournalGroup using same customized serialization causes error.
    Ref: https://anvil.works/docs/server/portable-classes/custom-serialisation#controlling-object-construction
    <Quote>
        If your __serialize__ implementation stores portable objects in global_data, make sure only to store objects that do not themselves require global_data. 
        (This can be because they don’t define a custom __serialize__ method, or because their __serialize__ method works OK when its global_data parameter is None.)
    </Quote>
    """
    # def __serialize__(self, global_data):
    #     global_data[f"{self.__class__.__name__}_{self.userid}_{self.get_group_id()}_{self.get_item_id()}"] = self.get_dict()
    #     return [self.userid, self.get_group_id(), self.get_item_id()]
    # 
    # def __deserialize__(self, key, global_data):
    #     userid, gid, iid = key
    #     data = global_data[f"{self.__class__.__name__}_{userid}_{gid}_{iid}"]
    #     self.__init__(data)

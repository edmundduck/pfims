import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import datetime as datetime
# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

class StockJournal:
    def __init__(self, data):
        self.set(data)

    def get(self):
        return [self.id, self.name, self.ccy, self.valid_from, self.valid_to, self.status]
        
    def set(self, data):
        if data and isinstance(data, list):
            self.iid = data[0]
            self.template_id = data[1]
            self.sell_date = data[2]
            self.buy_date = data[3]
            self.symbol = data[4]
            self.qty = data[5]
            self.sales = data[6]
            self.cost = data[7]
            self.fee = data[8]
            self.sell_price = data[9]
            self.buy_price = data[10]
            self.pnl = data[11]

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
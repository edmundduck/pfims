import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.
#
# To allow anvil.server.call() to call functions here, we mark
# them with @anvil.server.callable.
# Here is an example - you can replace it with your own:
#
# @anvil.server.callable
# def say_hello(name):
#   print("Hello, " + name + "!")
#   return 42
#
class journal():
    def __init__(self, tuple):
        self.iid = tuple.iid
        self.template_id = tuple.template_id
        self.sell_date = tuple.sell_date
        self.buy_date = tuple.buy_date
        self.symbol = tuple.symbol
        self.qty = int(tuple.qty)
        self.sales = float(tuple.sales)
        self.cost = float(tuple.cost)
        self.fee = float(tuple.fee)
        self.sell_price = float(tuple.sell_price)
        self.buy_price = float(tuple.buy_price)
        self.pnl = float(tuple.pnl)

    def __str__(self):
        return f"Journal(iid:{self.iid}, templ_id:{template_id}): {self.sell_date}, {self.buy_date}, \
            {self.symbol}, {self.qty}, {self.sales}, {self.cost}, {self.fee}, {self.sell_price}, {self.buy_price}, {self.pnl}"

    @anvil.server.callable
    def convertMapToTuple(self, dict):
        param_list = ['iid', 'template_id', 'sell_date', 'buy_date', 'symbol', 'qty', 'sales', 'cost', 'fee', 'sell_price', 'buy_price', 'pnl']
        tuple_list = []
        for item in param_list:
            tuple_list.append(dict[item])
        return tuple_list

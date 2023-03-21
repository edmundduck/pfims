import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from . import mod_debug

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
class TradeJournal:
    def __init__(self, tuple=None):
        self.attr = {}
        if tuple is not None:
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
        return f"TradeJournal(iid:{self.iid}, templ_id:{template_id}): {self.sell_date}, {self.buy_date}, \
            {self.symbol}, {self.qty}, {self.sales}, {self.cost}, {self.fee}, {self.sell_price}, {self.buy_price}, {self.pnl}"

    def getTuple(self):
        param_list = ['template_id', 'sell_date', 'buy_date', 'symbol', 'qty', 'sales', 'cost', 'fee', 'sell_price', 'buy_price', 'pnl']
        tuple_list = []
        for item in param_list:
            mod_debug.print_data_debug('param', item)
            tuple_list.append(str(self.attr.get(item)))
        return tuple_list

    def assignFromDict(self, dict):
        # self.iid = dict.get('iid') if dict.get('iid') is not None else self.iid
        # self.template_id = dict.get('template_id') if dict.get('template_id') is not None else self.template_id
        # self.sell_date = dict.get('sell_date') if dict.get('sell_date') is not None else self.sell_date
        # self.buy_date = dict.get('buy_date') if dict.get('buy_date') is not None else self.buy_date
        # self.symbol = dict.get('symbol') if dict.get('symbol') is not None else self.symbol
        # self.qty = dict.get('qty') if dict.get('qty') is not None else self.qty
        # self.sales = dict.get('sales') if dict.get('sales') is not None else self.sales
        # self.cost = dict.get('cost') if dict.get('cost') is not None else self.cost
        # self.fee = dict.get('fee') if dict.get('fee') is not None else self.fee
        # self.sell_price = dict.get('sell_price') if dict.get('sell_price') is not None else self.sell_price
        # self.buy_price = dict.get('buy_price') if dict.get('buy_price') is not None else self.buy_price
        # self.pnl = dict.get('pnl') if dict.get('pnl') is not None else self.pnl
        self.attr['iid'] = dict.get('iid') if dict.get('iid') is not None else self.attr.get('iid')
        self.attr['template_id'] = dict.get('template_id') if dict.get('template_id') is not None else self.attr.get('template_id')
        self.attr['sell_date'] = dict.get('sell_date') if dict.get('sell_date') is not None else self.attr.get('sell_date')
        self.attr['buy_date'] = dict.get('buy_date') if dict.get('buy_date') is not None else self.attr.get('buy_date')
        self.attr['symbol'] = dict.get('symbol') if dict.get('symbol') is not None else self.attr.get('symbol')
        self.attr['qty'] = dict.get('qty') if dict.get('qty') is not None else self.attr.get('qty')
        self.attr['sales'] = dict.get('sales') if dict.get('sales') is not None else self.attr.get('sales')
        self.attr['cost'] = dict.get('cost') if dict.get('cost') is not None else self.attr.get('cost')
        self.attr['fee'] = dict.get('fee') if dict.get('fee') is not None else self.attr.get('fee')
        self.attr['sell_price'] = dict.get('sell_price') if dict.get('sell_price') is not None else self.attr.get('sell_price')
        self.attr['buy_price'] = dict.get('buy_price') if dict.get('buy_price') is not None else self.attr.get('buy_price')
        self.attr['pnl'] = dict.get('pnl') if dict.get('pnl') is not None else self.attr.get('pnl')

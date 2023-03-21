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
    def __init__(self, attr=None):
        self.attr = attr if attr is not None else {}

    def __str__(self):
        return "{0} (iid:{1}, tid:{2}) - {3}, {4}, {5}, {6}, {7}, {8}, {9}, {10}, {11}, {12}".format(
            self.__class__,
            self.attr.get('iid'), \
            self.attr.get('template_id'), \
            self.attr.get('sell_date'), \
            self.attr.get('buy_date'), \
            self.attr.get('symbol'), \
            self.attr.get('qty'), \
            self.attr.get('sales'), \
            self.attr.get('cost'), \
            self.attr.get('fee'), \
            self.attr.get('sell_price'), \
            self.attr.get('buy_price'), \
            self.attr.get('pnl')
        )

    def getTuple(self):
        param_list = ['template_id', 'sell_date', 'buy_date', 'symbol', 'qty', 'sales', 'cost', 'fee', 'sell_price', 'buy_price', 'pnl']
        tuple_list = []
        for item in param_list:
            tuple_list.append(str(self.attr.get(item)))
        return tuple_list

    def assignFromDict(self, dict):
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
        return self
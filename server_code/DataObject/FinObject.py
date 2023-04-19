import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from ..System import SystemModule as sysmod

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
        param_list = ['iid', 'template_id', 'sell_date', 'buy_date', 'symbol', 'qty', 'sales', 'cost', 'fee', 'sell_price', 'buy_price', 'pnl']
        tuple_list = []
        for item in param_list:
            tuple_list.append(str(self.attr.get(item)))
        return tuple_list

    def assignFromDict(self, dict):
        for key in dict.keys():
            self.attr[key] = dict.get(key) if dict.get(key) is not None else (0 if key == 'iid' else '')
        return self

class CashTransaction:
    def __init__(self, attr=None):
        self.attr = attr if attr is not None else {}

    def __str__(self):
        return "{0} (iid:{1}, tid:{2}) - {3}, {4}, {5}, {6}, {7}, {8}".format(
            self.__class__,
            self.attr.get('iid'), \
            self.attr.get('tab_id'), \
            self.attr.get('trandate'), \
            self.attr.get('account_id'), \
            self.attr.get('amount'), \
            self.attr.get('labels'), \
            self.attr.get('remarks'), \
            self.attr.get('stmt_dtl')
        )

    # Return a record compatible for database operation in list type
    def getDatabaseRecord(self):
        param_list = ('iid', 'tab_id', 'trandate', 'account_id', 'amount', 'labels', 'remarks', 'stmt_dtl')
        tuple_list = []
        for item in param_list:
            tuple_list.append(self.attr.get(item)) 
        return tuple_list

    def assignFromDict(self, dict):
        for key in dict.keys():
            if key == 'labels': print("labels:", dict.get(key))
            self.attr[key] = dict.get(key) if dict.get(key) is not None else (0 if key == 'iid' else '')
        return self

    # Return False if any of the mandatory field value is None, otherwise True
    def isValidRecord(self):
        mandatory_list = ('trandate', 'account_id', 'amount')
        for item in mandatory_list:
            if self.attr.get(item) is None:
                return False
        return True
import anvil.files
from anvil.files import data_files
import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from ..SysProcess.Constants import ExpenseDBTableDefinion as exptbl
from ..SysProcess import LoggingModule

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.
logger = LoggingModule.ServerLogger()

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

    @logger.log_function
    def getTuple(self):
        param_list = ['iid', 'template_id', 'sell_date', 'buy_date', 'symbol', 'qty', 'sales', 'cost', 'fee', 'sell_price', 'buy_price', 'pnl']
        tuple_list = []
        for item in param_list:
            tuple_list.append(str(self.attr.get(item)))
        return tuple_list

    @logger.log_function
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
            self.attr.get(exptbl.Date), \
            self.attr.get(exptbl.Account), \
            self.attr.get(exptbl.Amount), \
            self.attr.get(exptbl.Labels), \
            self.attr.get(exptbl.Remarks), \
            self.attr.get(exptbl.StmtDtl)
        )

    # Return a record compatible for database operation in list type
    @logger.log_function
    def getDatabaseRecord(self):
        param_list = ('iid', 'tab_id', \
                      exptbl.Date, \
                      exptbl.Account, \
                      exptbl.Amount, \
                      exptbl.Labels, \
                      exptbl.Remarks, \
                      exptbl.StmtDtl)
        tuple_list = []
        for item in param_list:
            i = self.attr.get(item)[0] if isinstance(self.attr.get(item), list) else self.attr.get(item)
            tuple_list.append(i)
        return tuple_list

    @logger.log_function
    def assignFromDict(self, dict):
        for key in dict.keys():
            if dict.get(key) is not None:
                self.attr[key] = dict.get(key)
            else:
                (0 if key == 'iid' else '')
        return self

    # Return False if any of the mandatory field value is None, otherwise True
    @logger.log_function
    def isValidRecord(self):
        mandatory_list = (exptbl.Date, exptbl.Account, exptbl.Amount)
        for item in mandatory_list:
            if self.attr.get(item) is None:
                return False
        return True
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

    def assignFromDict(self, dict):
        for key in dict.keys():
            self.attr[key] = dict.get(key) if dict.get(key) is not None else (0 if key == 'iid' else '')
        return self

class ExpenseRecord:

    # Class variables
    IID = 'iid'
    TID = 'tab_id'
    Date = 'DTE'
    Account = 'ACC'
    Amount = 'AMT'
    Remarks = 'RMK'
    StmtDtl = 'STD'
    Labels = 'LBL'
    data_list = (Date, Account, Amount, Remarks, StmtDtl, Labels)
    column_list = (IID, TID, Date, Account, Amount, Labels, Remarks, StmtDtl)

    @staticmethod
    @anvil.server.callable
    def blankexprecord():
        """
        Return a blank record with all keys required by an expense record exist and None in value in dict.
    
        Returns:
            dict: A dict with all keys exist, while value are None.
        """
        return {c: None for c in ExpenseRecord.column_list}
    
    def __init__(self, attr=None):
        self.attr = {}
        self.attr = self.assignval(attr)

    def __str__(self):
        return "{0} (iid:{1}, tid:{2}) - {3}, {4}, {5}, {6}, {7}, {8}".format(
            self.__class__,
            self.attr.get(self.IID), \
            self.attr.get(self.TID), \
            self.attr.get(self.Date), \
            self.attr.get(self.Account), \
            self.attr.get(self.Amount), \
            self.attr.get(self.Labels), \
            self.attr.get(self.Remarks), \
            self.attr.get(self.StmtDtl)
        )

    # Return a record compatible for database operation in list type
    @logger.log_function
    def getDatabaseRecord(self):
        tuple_list = []
        for item in self.column_list:
            i = self.attr.get(item)[0] if isinstance(self.attr.get(item), list) else self.attr.get(item)
            if i is None:
                tuple_list.append(i)
            else:
                tuple_list.append(str(i))
        return tuple_list

    def assignval(self, dict):
        """
        Assign value according to the key.

        If a key not belonging to the column definition, KeyError will be raised.
        
        Parameters:
            dict (dict): A dictionary containing keys which is/are one of the column definitions.
    
        Returns:
            attr_copy (dict): Return a copy of the updated ExpenseRecord record.
        """
        attr_copy = self.attr.copy() if self.attr is not None else {}
        if dict is not None:
            for key in dict.keys():
                if key in self.column_list:
                    if key == self.IID:
                        attr_copy[key] = dict.get(key) if dict.get(key) is not None else 0
                    else:
                        attr_copy[key] = dict.get(key)
                else:
                    raise KeyException(f"Key not belonging to ")
        return attr_copy

    def isvalid(self):
        """
        Return False if any of the mandatory field value is None, otherwise True.
    
        Returns:
            boolean: Return True only when all the mandatory field values are not None.
        """
        mandatory_list = (exptbl.Date, exptbl.Account, exptbl.Amount)
        for item in mandatory_list:
            if self.attr.get(item) is None:
                return False
        return True
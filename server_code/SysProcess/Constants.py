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

# Config for Setting page
# Database col definition change may be required should the values are adjusted here
class SettingConfig:
    BROKER_ID_PREFIX = 'BR'
    BROKER_SUFFIX_LEN = 5

# Expense table definition for data transformation required in expense input file import
class ExpenseDBTableDefinion:
    Date = 'trandate'
    Account = 'account_id'
    Amount = 'amount'
    Remarks = 'remarks'
    StmtDtl = 'stmt_dtl'
    Labels = 'labels'
    def_namelist = [Date, Account, Amount, Remarks, StmtDtl, Labels]
    defmap = {
        'D': Date, 
        'AC': Account, 
        'AM': Amount, 
        'R': Remarks, 
        'SD': StmtDtl, 
        'L': Labels
    }

# Search interval modes used in Report search panel and config
class SearchInterval:
    INTERVAL_LAST_1_MTH = 'L1M'
    INTERVAL_LAST_3_MTH = 'L3M'
    INTERVAL_LAST_6_MTH = 'L6M'
    INTERVAL_LAST_1_YR = 'L1Y'
    INTERVAL_YEAR_TO_DATE = 'YTD'
    INTERVAL_SELF_DEFINED = 'SDR'

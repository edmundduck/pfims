import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.

class SettingConfig:
    """
    Config for Setting page.

    Database col definition change may be required should the values are adjusted here.
    """
    BROKER_ID_PREFIX = 'BR'
    BROKER_SUFFIX_LEN = 5

class ExpenseDBTableDefinion:
    """
    Expense table definition for data transformation required in expense input file import.
    """
    Date = 'DTE'
    Account = 'ACC'
    Amount = 'AMT'
    Remarks = 'RMK'
    StmtDtl = 'STD'
    Labels = 'LBL'
    def_namelist = [Date, Account, Amount, Remarks, StmtDtl, Labels]

class SearchInterval:
    """
    Search interval modes used in Report search panel and config.
    """
    INTERVAL_LAST_1_MTH = 'L1M'
    INTERVAL_LAST_3_MTH = 'L3M'
    INTERVAL_LAST_6_MTH = 'L6M'
    INTERVAL_LAST_1_YR = 'L1Y'
    INTERVAL_YEAR_TO_DATE = 'YTD'
    INTERVAL_SELF_DEFINED = 'SDR'

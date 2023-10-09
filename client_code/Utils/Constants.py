import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

class CacheKey:
    """
    Non-function keys for client cache.
    """
    STOCK_INPUT_DEL_IID = 'stock_input_delete_row_iid'
    EXP_INPUT_DEL_IID = 'exp_input_delete_row_iid'
    
class ExpenseConfig:
    """
    Config for Input Expense page.
    """
    DEFAULT_ROW_NUM = 10
    BUTTON_SUBMIT_TEXT = 'SUBMIT TAB'
    BUTTON_DRAFT_TEXT = 'SAVE DRAFT'

# TODO - This has to be in sync with server one, and to be removed once a consolidated solution is found
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
    def_list = [Date, Account, Amount, Remarks, StmtDtl, Labels]    

class FileImportType:
    """
    File import type.
    """
    Excel = 'E'
    PDF = 'P'

class FileImportLabelExtraAction:
    """
    Label mapping extra action required by Excel file import.
    """
    SKIP = 'S'
    MAP = 'M'
    CREATE = 'C'

class ReportSearchMode:
    USER_DEFINED = 'SDR'

# PnL reports drill mode
class PNLDrillMode:
    """
    Different drill mode for PnL reporting.
    """
    DAY = 'd'
    MONTH = 'm'
    YEAR = 'y'

class LoggingLevel:
    """
    Logging levels used in setting.
    """
    dropdown = [('TRACE', 5), ('DEBUG', 10), ('INFO', 20), ('WARNING', 30), ('ERROR', 40), ('CRITICAL', 50)]

class Icons:
    """
    Icons definition used in the UI.
    """
    BULLETPOINT = 'fa:info'
    DATA_DRILLDOWN = 'fa:plus-square'
    DATA_SUMMARIZE = 'fa:minus-square'
    MENU_EXPAND = 'fa:caret-down'
    MENU_SHRINK = 'fa:caret-right'
    REMOVE = 'fa:minus'

class ColorSchemes:
    """
    Color definition used in the UI.
    """
    VALID_ERROR = 'rgb(245,135,200)'
    VALID_NORMAL = 'rgb(250,250,250)'
    BUTTON_FG = 'White'
    BUTTON_BG = 'Blue'
    AMT_NEG = 'Red'
    AMT_POS = 'Green'
    AMT_EXPENSE = 'Black'
    THEME_PRIM = 'theme:Primary 500'
    THEME_SEC = 'theme:Secondary 500'
    THEME_WHITE = 'theme:White'

class Alerts:
    """
    Constants used in alerts.
    """
    CONFIRM = 'Y'
    CANCEL = 'N'
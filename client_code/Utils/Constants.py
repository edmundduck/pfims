import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

# Config for Setting page
# Database col definition change may be required should the values are adjusted here
class SettingConfig:
    BROKER_ID_PREFIX = 'BR'
    BROKER_SUFFIX_LEN = 5

# Config for Input Expense page
class ExpenseConfig:
    DEFAULT_ROW_NUM = 10
    BUTTON_SUBMIT_TEXT = 'SUBMIT TAB'
    BUTTON_DRAFT_TEXT = 'SAVE DRAFT'

class FileUploadLabelExtraAction:
    SKIP = 'S'
    MAP = 'M'
    CREATE = 'C'

# PnL reports drill mode
class PNLDrillMode:
    DAY = 'd'
    MONTH = 'm'
    YEAR = 'y'

class Icons:
    BULLETPOINT = 'fa:info'
    DATA_DRILLDOWN = 'fa:plus-square'
    DATA_SUMMARIZE = 'fa:minus-square'
    MENU_EXPAND = 'fa:caret-down'
    MENU_SHRINK = 'fa:caret-right'
    REMOVE = 'fa:minus'

class ColorSchemes:
    VALID_ERROR = 'rgb(245,135,200)'
    THEME_PRIM = 'theme:Primary 500'
    THEME_SEC = 'theme:Secondary 500'
    THEME_WHITE = 'theme:White'

class Alerts:
    CONFIRM = 'Y'
    CANCEL = 'N'
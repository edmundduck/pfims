import anvil.server
# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

class CacheExpiry:
    """
    Expiry for cache in minutes
    """
    MINUTES = 15

class CacheKey:
    """
    Keys for dropdowns
    """
    DD_ACCOUNT = 'accounts_dropdown'
    DD_BROKER = 'broker_dropdown'
    DD_CURRENCY = 'ccy_dropdown'
    DD_EXPENSE_TAB = 'expense_groups_dropdown'
    DD_EXPENSE_TBL_DEF = 'expense_table_definition_dropdown'
    DD_IMPORT_EXTRA_ACTION = 'upload_action_dropdown'
    DD_IMPORT_FILE_TYPE = 'mapping_type_dropdown'
    # DD_IMPORT_MAPPING_GRP = 'mapping_dropdown'
    DD_LABEL = 'labels_dropdown'
    DD_LABEL_MAPPING_ACTION = 'labels_mapping_action_dropdown'
    DD_SEARCH_INTERVAL = 'search_interval_dropdown'
    DD_STOCK_JRN_GRP = 'stock_journal_group_dropdown'
    DD_SUBMITTED_JRN_GRP = 'submitted_journal_group_dropdown'

    """
    Keys for dicts
    """
    DICT_LABEL_LIST = DD_LABEL
    DICT_LABEL = 'labels_dict'
    
    """
    Keys for objects
    """
    OBJ_ACCOUNT = 'account_object'
    OBJ_EXPENSE_GRP = 'expense_transaction_group_object'
    OBJ_LABEL = 'label_object'
    OBJ_STOCK_JRN_GRP = 'stock_journal_group_object'

    """
    Keys for deletion IID cache list
    """
    STOCK_INPUT_DEL_IID = 'stock_input_delete_row_iid'
    EXP_INPUT_DEL_IID = 'exp_input_delete_row_iid'

class CacheDropdown:
    DROPDOWN_MAPPPING = {
        CacheKey.DD_ACCOUNT: ['generate_accounts_list', lambda d: list((r['name'] + " (" + str(r['id']) + ")", [r['id'], r['name']]) for r in d)],
        CacheKey.DD_BROKER: ['generate_brokers_simplified_list', lambda d: list((''.join([r['name'], ' [', r['ccy'], ']']), (r['broker_id'], r['name'], r['ccy'])) for r in d)],
        CacheKey.DD_CURRENCY: ['generate_currency_list', lambda d: list((r['abbv'] + " " + r['name'] + " (" + r['symbol'] + ")" if r['symbol'] else r['abbv'] + " " + r['name'], r['abbv']) for r in d)],
        CacheKey.DD_EXPENSE_TAB: ['generate_expense_groups_list', lambda d: list((r['tab_name'] + ' (' + str(r['tab_id']) + ')', [r['tab_id'], r['tab_name']]) for r in d)],
        CacheKey.DD_EXPENSE_TBL_DEF: ['generate_expense_tbl_def_list', lambda d: list((r['col_name'], [r['col_code'], r['col_name']]) for r in d)],
        CacheKey.DD_IMPORT_EXTRA_ACTION: ['generate_upload_action_list', lambda d: list((r['action'], [r['id'], r['action']]) for r in d)],
        CacheKey.DD_IMPORT_FILE_TYPE: ['generate_mapping_type_list', lambda d: list((r['name'], [r['id'], r['name']]) for r in d)],
        # CacheKey.DD_IMPORT_MAPPING_GRP: ['generate_mapping_list', lambda d: list((r['name'], r['id']) for r in d)],
        CacheKey.DD_LABEL: ['generate_labels_list', lambda d: list((r['name'] + " (" + str(r['id']) + ")", (r['id'], r['name'])) for r in d)],
        CacheKey.DD_LABEL_MAPPING_ACTION: ['generate_labels_mapping_action_list', lambda d: list((r['action'], [r['id'], r['action']]) for r in d)],
        CacheKey.DD_SEARCH_INTERVAL: ['generate_search_interval_list', lambda d: list((r['name'], r['id']) for r in d)], 
        CacheKey.DD_STOCK_JRN_GRP: ['generate_drafting_stock_journal_groups_list', lambda d: list((''.join([r['template_name'], ' [', str(r['template_id']), ']']), (r['template_id'], r['template_name'])) for r in d)],
        CacheKey.DD_SUBMITTED_JRN_GRP: ['generate_submitted_journal_groups_list', lambda d: list((''.join([r['template_name'], ' [', str(r['template_id']), ']']), (r['template_id'], r['template_name'])) for r in d)]
    }

class SettingConfig:
    """
    Config for Setting page.

    Database col definition change may be required should the values are adjusted here.
    """
    BROKER_ID_PREFIX = 'BR'
    BROKER_SUFFIX_LEN = 5

class ExpenseConfig:
    """
    Config for Input Expense page.
    """
    DEFAULT_ROW_NUM = 5
    BUTTON_SUBMIT_TEXT = 'SUBMIT TAB'
    BUTTON_DRAFT_TEXT = 'SAVE DRAFT'

class FileImportType:
    """
    File import type.
    """
    Excel = 'E'
    PDF = 'P'

class FileImportLabelMappingExtraAction:
    """
    Label mapping extra action required by Excel file import.
    """
    SKIP = 'S'
    MAP = 'M'
    CREATE = 'C'

class FileImportExcelColumnMappingExtraAction:
    """
    Excel column mapping extra action required by Excel file import.
    """
    LABEL = 'L'
    ACCOUNT = 'A'

class UploadMappingRulesInput:
    """
    Dictionsary keys of upload mapping rules.
    """
    EXCEL_COL= 'excelcol'
    DATA_COL = 'datacol'
    ACTION = 'action'
    ACCOUNT = 'acct'
    LABEL = 'lbl'

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

# PnL reports drill mode
class PNLDrillMode:
    """
    Different drill mode for PnL reporting.
    """
    DAY = 'd'
    MONTH = 'm'
    YEAR = 'y'

class ExpenseReportType:
    """
    Expense report type.
    """
    EXP_PER_LABEL = 'TEL'
    BAL_ACCT = 'BOA'
    droppdown = [('Total Expense per Label', EXP_PER_LABEL), ('Balance on Account', BAL_ACCT)]

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

class Roles:
    """
    Roles used in the UI together with CSS.
    """
    AMT_NEGATIVE = 'negative-amount-label'
    AMT_POSITIVE = 'positive-amount-label'
    BUTTON_REMOVAL = 'button-removal'
    VALID_ERROR = 'input-error'
    VALID_NORMAL = None
    LABEL = 'app-label-button'

class Alerts:
    """
    Constants used in alerts.
    """
    CONFIRM = 'Y'
    CANCEL = 'N'

class Database:
    """
    Settings used in database layer.
    """
    SCHEMA_FIN = 'fin'
    SCHEMA_REFDATA = 'refdata'

class LinkRole:
    """
    Role used in Link components to distinguish they are selected or not.
    """
    SELECTED = 'selected'
    UNSELECTED = None

class ReportFormTag:
    """
    Identification tag for report forms.
    """
    REPORT_TAG = 'rpttag'
    EXP_LIST_RPT = 'exprpt01'
    EXP_ANALYSIS_RPT = 'exprpt02'
    STOCK_TXN_RPT = 'stockrpt01'
    STOCK_PNL_RPT = 'stockrpt02'

class UnitTest:
    SUCCESS_CNT = 'success_count'
    FAIL_CNT = 'failure_count'
    FAIL_MSG = 'failure_messages'
    DELIMITER = ":="
    DELIMITER_FUNC = ","
    CLIENT_ONLY = "# Client code testing"
    SERVER_ONLY = "# Server code testing"
    TEST_CONFIG_FILE = 'unittest.conf'
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

""" === Validation functions === """
def validation_errfield_colour():
    return 'rgb(245,135,200)'

""" === Settings functions === """
def setting_ccy_dropdown():
    ccy_list = [('$ USD', 'USD'), 
                ('£ GBP', 'GBP'), 
                ('$ HKD', 'HKD'),
                ('€ EUR', 'EUR')]
    return ccy_list

def setting_broker_id_prefix():
    return "BR"

def setting_broker_suffix_len():
    return 5

def setting_broker_dropdown():
    broker_list = [('[Select to update or delete]', '')]
    return broker_list

def search_interval_dropdown():
    interval_list = [('[Interval]', ''), 
                    ('Last 1 Month', 'L1M'), 
                    ('Last 3 Month', 'L3M'),
                    ('Last 6 Month', 'L6M'),
                    ('Last 1 Year', 'L1Y'),
                    ('Year to Date', 'YTD'),
                    ('Self Defined Range', 'SDR')]
    return interval_list

def search_symbol_dropdown():
    symbol_list = [('[Symbol]', '')]
    return symbol_list

def form_poc1():
    return 'form_poc1'

""" === Input expense functions === """
def input_expense_row_size():
    return 10

def input_expense_col_def():
    col_def = [('Date', 'D'), 
                ('Account', 'AC'), 
                ('Amount', 'AM'),
                ('Labels', 'L'),
                ('Remarks', 'R'),
                ('Statement Detail', 'SD')]
    return col_def

""" === PNL report functions === """
def pnl_list_day_mode():
    return 'd'

def pnl_list_mth_mode():
    return 'm'

def pnl_list_yr_mode():
    return 'y'

def pnl_list_expand_icon():
    return 'fa:plus-square'

def pnl_list_shrink_icon():
    return 'fa:minus-square'

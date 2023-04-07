import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:
#
#    from . import Module1
#
#    Module1.say_hello()
#

del_iid = []
input_stock_templ_chg = False
input_stock_jour_chg = False

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

# === Input stock functions ===
def input_stock_default_templ_dropdown():
    return "[NEW]"

def input_stock_default_templ_name():
    return "NewTemplate"

# Add IID into the deletion list for delete journals function to process
def add_deleted_row(iid):
    global del_iid
    del_iid.append(iid)

# Reset the deletion list
def reset_deleted_row():
    global del_iid
    del_iid = []

# Track template fields change
def track_input_stock_template_change():
    global input_stock_templ_chg
    input_stock_templ_chg = True

# Track journals fields change
def track_input_stock_journals_change():
    global input_stock_jour_chg
    input_stock_jour_chg = True

# Reset template and journals fields change
def reset_input_stock_change():
    global input_stock_templ_chg, input_stock_jour_chg
    input_stock_templ_chg = False
    input_stock_jour_chg = False

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

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

def form_lv2_tranx_list():
  return 'form_lv2_tranx_list'

def form_lv2_pnl_report():
  return 'form_lv2_pnl_report'

def form_poc1():
  return 'form_poc1'

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

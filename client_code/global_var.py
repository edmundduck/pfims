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

cache_dict_day = None
cache_dict_mth = None
cache_dict_yr = None

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

def get_pnl_dictcache():
  return cache_dict_day, cache_dict_mth, cache_dict_yr

def set_pnl_dictcache(daycache, mthcache, yrcache):
  cache_dict_day = daycache
  cache_dict_mth = mthcache
  cache_dict_yr = yrcache

def init_pnl_dictcache():
  cache_dict_day, cache_dict_mth, cache_dict_yr = None
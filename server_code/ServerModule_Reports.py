import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from datetime import date, datetime, timedelta

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

# Static variables
INTERVAL_LAST_1_MTH = "L1M"
INTERVAL_LAST_3_MTH = "L3M"
INTERVAL_LAST_6_MTH = "L6M"
INTERVAL_LAST_1_YR = "L1Y"
INTERVAL_YEAR_TO_DATE = "YTD"

# Internal function - Return start date of last 1 month
def get_L1M_start_date(end_date):
  if end_date.month-1 < 1:
    return date(end_date.year-1, end_date.month+12-1, end_date.day)
  else:
    return date(end_date.year, end_date.month+-1, end_date.day)

# Internal function - Return start date of last 3 months
def get_L3M_start_date(end_date):
  if end_date.month-3 < 1:
    return date(end_date.year-1, end_date.month+12-3, end_date.day)
  else:
    return date(end_date.year, end_date.month-3, end_date.day)

# Internal function - Return start date of last 6 months
def get_L6M_start_date(end_date):
  if end_date.month-6 < 1:
    return date(end_date.year-1, end_date.month+12-6, end_date.day)
  else:
    return date(end_date.year, end_date.month-6, end_date.day)

# Internal function - Return start date of last 1 year
def get_L1Y_start_date(end_date):
  return date(end_date.year-1, end_date.month, end_date.day)

# Internal function - Return the 1st date of the current year
def get_YTD_start_date(end_date):
  return date(end_date.year, 1, 1)

# Internal function - Return None if it's not date
def interval_default(end_date):
  return None

@anvil.server.callable
# Get all symbols which were transacted between start and end date into the dropdown
def get_symbol_dropdown_items(end_date, start_date):
  if end_date is not None and start_date is not None:
    return list(sorted(set(row['symbol'] for row in app_tables.templ_journals.search(sell_date=q.less_than(end_date), buy_date=q.greater_than(start_date)))))
  else:
    return []

@anvil.server.callable
# Get start date based on end date and time interval dropdown value
def get_start_date(end_date, interval):
  switcher = {
    INTERVAL_LAST_1_MTH: get_L1M_start_date,
    INTERVAL_LAST_3_MTH: get_L3M_start_date,
    INTERVAL_LAST_6_MTH: get_L6M_start_date,
    INTERVAL_LAST_1_YR: get_L1Y_start_date,
    INTERVAL_YEAR_TO_DATE: get_YTD_start_date,
  }
  
  return switcher.get(interval, interval_default)(end_date)

@anvil.server.callable
# DB table "templ_journals" select method
def select_templ_journals(end_date, start_date, symbols):
  if len(symbols) > 0:
    return app_tables.templ_journals.search(sell_date=q.less_than_or_equal_to(end_date), 
                                            buy_date=q.greater_than_or_equal_to(start_date),
                                            symbol=q.any_of(*symbols))
  else:
    return app_tables.templ_journals.search(sell_date=q.less_than_or_equal_to(end_date), 
                                            buy_date=q.greater_than_or_equal_to(start_date))

@anvil.server.callable
# Return rows of P&L by selecting and compiling DB table "templ_journals" data
def select_pnl_data(end_date, start_date, symbols):
  rows = None
  if len(symbols) > 0:
    rows = app_tables.templ_journals.search(sell_date=q.less_than_or_equal_to(end_date), 
                                            buy_date=q.greater_than_or_equal_to(start_date),
                                            symbol=q.any_of(*symbols))
  else:
    rows = app_tables.templ_journals.search(sell_date=q.between(start_date, end_date, max_inclusive=True))

  # Prepare the data in dictionary structure
  dictstruct = {}
  for i in rows:
    # Key has to be in string instead of datetime obj
    sell_date_str = i['sell_date'].strftime("%Y-%m-%d")
    # Debug
    #print("sell={} / buy={} / diff={}".format(i['sell_date'], i['buy_date'], (i['sell_date']-i['buy_date']).days))

    numtrade, numdaytrade, sales, cost, fee, pnl = dictstruct.get(sell_date_str, [0, 0, 0, 0, 0, 0])
    if (i['sell_date'] - i['buy_date']).days == 0:
      numdaytrade += 1
    else:
      numtrade += 1
    sales += i['sales']
    cost += i['cost']
    fee += i['fee']
    pnl += i['pnl']
    dictstruct.update({sell_date_str: [numtrade, numdaytrade, sales, cost, fee, pnl]})

  # Reformat dictionary structure data into repeatingpanel compatible data (dict in list)
  rowstruct = []
  for j in dictstruct.keys():
    numtrade, numdaytrade, sales, cost, fee, pnl = dictstruct.get(j)
    dictitem = {
      'sell_date': j,
      'num_trade': numtrade,
      'num_daytrade': numdaytrade,
      'sales': sales,
      'cost': cost,
      'fee': fee,
      'pnl': pnl
    }
    rowstruct += [dictitem]
  return rowstruct

# Internal function - Build P&L dictionary in day, month and year aspects
# rowitem = Items in rows returned from DB table 'templ_journals' search result
def format_pnl_dict(rowitem, dictupdate, key, parentkey, mode):
  numtrade, numdaytrade, sales, cost, fee, pnl, parent = dictupdate.get(key, [0, 0, 0, 0, 0, 0, ''])
  if (rowitem['sell_date'] - rowitem['buy_date']).days == 0:
    numdaytrade += 1
  else:
    numtrade += 1
  sales += rowitem['sales']
  cost += rowitem['cost']
  fee += rowitem['fee']
  pnl += rowitem['pnl']
  parent = parentkey
  mod = mode
  dictupdate.update({key: [numtrade, numdaytrade, sales, cost, fee, pnl, parentkey, mode]})
  return dictupdate

@anvil.server.callable
def format_pnl_data(end_date, start_date, symbols):
  rows = None
  if len(symbols) > 0:
    rows = app_tables.templ_journals.search(sell_date=q.less_than_or_equal_to(end_date), 
                                            buy_date=q.greater_than_or_equal_to(start_date),
                                            symbol=q.any_of(*symbols))
  else:
    rows = app_tables.templ_journals.search(sell_date=q.between(start_date, end_date, max_inclusive=True))

  # Prepare the data in dictionary structure
  dictstruct_day = {}
  dictstruct_mth = {}
  dictstruct_yr = {}
  for i in rows:
    # Key has to be in string instead of datetime obj
    sell_date_str = i['sell_date'].strftime("%Y-%m-%d")
    sell_mth_str = i['sell_date'].strftime("%Y-%m")
    sell_yr_str = i['sell_date'].strftime("%Y")
    # Debug
    #print("sell={} / buy={} / diff={}".format(i['sell_date'], i['buy_date'], (i['sell_date']-i['buy_date']).days))
    
    # Handling of Day
    dictstruct_day = format_pnl_dict(i, dictstruct_day, sell_date_str, sell_mth_str, 'd')
    
    # Handling of Month
    dictstruct_mth = format_pnl_dict(i, dictstruct_mth, sell_mth_str, sell_yr_str, 'm')

    # Handling of Year
    dictstruct_yr = format_pnl_dict(i, dictstruct_yr, sell_yr_str, '', 'y')

  # TODO DEBUG
  print("dictstruct_day = {}".format(dictstruct_day))
  print("dictstruct_mth = {}".format(dictstruct_mth))
  print("dictstruct_yr = {}".format(dictstruct_yr))

  # Reformat dictionary structure data into repeatingpanel compatible data (dict in list)
  rowstruct = []
  for j in dictstruct.keys():
    numtrade, numdaytrade, sales, cost, fee, pnl = dictstruct.get(j)
    dictitem = {
      'sell_date': j,
      'num_trade': numtrade,
      'num_daytrade': numdaytrade,
      'sales': sales,
      'cost': cost,
      'fee': fee,
      'pnl': pnl
    }
    rowstruct += [dictitem]
  return rowstruct

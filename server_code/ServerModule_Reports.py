import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from datetime import date, timedelta

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
  end_date = date(end_date.year, end_date.month-8, end_date.day)
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
  # TODO DEBUG
  print(end_date, start_date)
  if start_date is not None:
    return list(sorted(set(row['symbol'] for row in app_tables.temp_input.search(sell_date=q.less_than(end_date), buy_date=q.greater_than(start_date)))))
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

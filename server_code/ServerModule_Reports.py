import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from datetime import date, timedelta
# Following is not available in free plan
#from dateutil.relativedelta import relativedelta

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
  print(end_date - timedelta(days=30))

# Internal function - Return start date of last 3 months
def get_L3M_start_date(end_date):
  print(end_date - timedelta(days=90))

# Internal function - Return start date of last 6 months
def get_L6M_start_date(end_date):
  print(end_date - timedelta(days=180))

# Internal function - Return start date of last 1 year
def get_L1Y_start_date(end_date):
  print(date(en) - timedelta(days=365))

# Internal function - Return the 1st date of the current year
def get_YTD_start_date(end_date):
  print(date(end_date.year, 1, 1))

@anvil.server.callable
#
def get_symbol_dropdown_items():
  pass

@anvil.server.callable
# Get start date based on end date and time interval dropdown value
def get_start_date(end_date, interval):
  switcher = {
    INTERVAL_LAST_1_MTH: get_L1M_start_date,
    INTERVAL_LAST_3_MTH: get_L3M_start_date,
    INTERVAL_LAST_6_MTH: get_L6M_start_date,
    INTERVAL_LAST_1_YR: get_L1Y_start_date,
    INTERVAL_YEAR_TO_DATE: get_YTD_start_date
  }
  
  switcher.get(interval, "")(end_date)

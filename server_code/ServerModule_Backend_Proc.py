import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

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
    if dictstruct.get(sell_date_str, None) is None:
      if (i['sell_date'] - i['buy_date']).days == 0:
        dictstruct.update({sell_date_str: [0, 1, i['sales'], i['cost'], i['fee'], i['pnl']]})
      else:
        dictstruct.update({sell_date_str: [1, 0, i['sales'], i['cost'], i['fee'], i['pnl']]})
    else:
      numtrade, numdaytrade, sales, cost, fee, pnl = dictstruct.get(sell_date_str)
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

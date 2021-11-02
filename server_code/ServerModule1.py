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
def add_temp_input(date_sales, date_buy, symbol, qty, sales, cost, pnl, sell_price, buy_price):
  app_tables.temp_input.add_row(date_sales=date_sales,
                                date_buy=date_buy,
                                symbol=symbol,
                                qty=qty,
                                sales=sales,
                                cost=cost,
                                pnl=pnl,
                                sell_price=sell_price,
                                buy_price=buy_price)
  
@anvil.server.callable
def update_generate_input_templ_name(templ_choice_id):
    if templ_choice_id == "[New]":
      return "NewTemplate001"
    else:
      return app_tables.temp_template.get(template_id=templ_choice_id)
    
@anvil.server.callable
def get_input_templ_list():
  return app_tables.temp_template.
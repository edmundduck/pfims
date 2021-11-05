import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import random
import string
from datetime import date, datetime

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
RANDOM_ID_ALPHA_LEN = 4
DEFAULT_NEW_TEMPL_TEXT = "[NEW]"
DEFAULT_NEW_TEMPL_NAME = "NewTemplate"

@anvil.server.callable
def upsert_temp_input(sell_date, buy_date, template_id, symbol, qty, sales, cost, pnl, sell_price, buy_price):
  app_tables.temp_input.add_row(sell_date=sell_date,
                                buy_date=buy_date,
                                template_id=template_id, 
                                symbol=symbol,
                                qty=qty,
                                sales=sales,
                                cost=cost,
                                pnl=pnl,
                                sell_price=sell_price,
                                buy_price=buy_price)

@anvil.server.callable
def upsert_temp_template(template_id, template_name):
  row = app_tables.temp_template.get(template_id=template_id) or app_tables.temp_template.add_row(template_id=template_id,
                                                                                                  template_name=template_name)
  currenttime = datetime.now()
  row['template_create'] = currenttime if row['template_create'] is None else row['template_create']
  row['template_lastsave'] = currenttime

@anvil.server.callable
# 4 alphabets + 1 digit = 26^4 * 9 combinations
def generate_new_templ_id():
  new_id = ''.join(random.choice(string.ascii_uppercase) for x in range(RANDOM_ID_ALPHA_LEN)) + str(random.randint(0,9))
  while app_tables.temp_template.get(template_id=new_id) is not None:
    new_id = ''.join(random.choice(string.ascii_uppercase) for x in range(RANDOM_ID_ALPHA_LEN)) + str(random.randint(0,9))
  return new_id

@anvil.server.callable
def get_input_templ_name(templ_choice_str):
  if templ_choice_str is None or templ_choice_str == DEFAULT_NEW_TEMPL_TEXT:
    return DEFAULT_NEW_TEMPL_NAME
  else:
    templ_choice_id = templ_choice_str[:templ_choice_str.find("-")].strip()
    row = app_tables.temp_template.get(template_id=templ_choice_id)
    return row['template_name'] if row is not None else DEFAULT_NEW_TEMPL_NAME
    
@anvil.server.callable
def get_input_templ_list():
  content = list(str(row['template_id']) + " - " + row['template_name'] for row in app_tables.temp_template.search())
  content.insert(0, DEFAULT_NEW_TEMPL_TEXT)
  return content
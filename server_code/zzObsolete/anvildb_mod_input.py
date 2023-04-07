import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import random
import string
from datetime import date, datetime
from ..App import Global as glo
from ..AdminProcess import ConfigModule as cfmod
from ..System import SystemModule as sysmod

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

# # Static variables
# RANDOM_ID_ALPHA_LEN = 4

# # Internal function - Retrieve template ID by splitting template dropdown value
# def split_templ_id(templ_id):
#     if templ_id.find("-") < 0:
#         return templ_id
#     else:
#         return templ_id[:templ_id.find("-")].strip()

# @anvil.server.callable
# # Generate template dropdown text for display
# def generate_template_dropdown_item(templ_id, templ_name):
#     return templ_id + " - " + templ_name

# @anvil.server.callable
# # DB table "templ_journals" update/insert method
# def upsert_journals(iid, template_id, sell_date, buy_date, symbol, qty, sales, cost, fee, sell_price, buy_price, pnl):
#     rows = app_tables.templ_journals.search(template_id=template_id, iid=iid)
#     if len(list(rows)) != 0:
#         for r in rows:
#             r.update(
#                 iid=iid, 
#                 template_id=template_id, 
#                 sell_date=sell_date, 
#                 buy_date=buy_date, 
#                 symbol=symbol, 
#                 qty=int(qty), 
#                 sales=float(sales), 
#                 cost=float(cost), 
#                 fee=float(fee), 
#                 sell_price=float(sell_price), 
#                 buy_price=float(buy_price), 
#                 pnl=float(pnl))
#     else:
#         app_tables.templ_journals.add_row(
#             iid=iid, 
#             template_id=template_id, 
#             sell_date=sell_date,
#             buy_date=buy_date,
#             symbol=symbol,
#             qty=int(qty),
#             sales=float(sales),
#             cost=float(cost),
#             fee=float(fee),
#             sell_price=float(sell_price),
#             buy_price=float(buy_price), 
#             pnl=float(pnl))
    
# @anvil.server.callable
# # DB table "templ_journals" delete method
# def delete_journals(template_id):
#     rows = app_tables.templ_journals.search(template_id=template_id)
#     if len(list(rows)) != 0:
#         for r in rows:
#             r.delete()

# @anvil.server.callable
# # DB table "templates" update/insert method for save with time handling logic
# def save_templates(template_id, template_name, broker_id):
#     row = app_tables.templates.get(template_id=template_id) or app_tables.templates.add_row(template_id=template_id)
#     row['template_name'] = template_name
#     row['broker_id'] = broker_id
#     row['submitted'] = False if row['submitted'] is None else row['submitted']
#     currenttime = datetime.now()
#     row['template_create'] = currenttime if row['template_create'] is None else row['template_create']
#     row['template_lastsave'] = currenttime

# @anvil.server.callable
# # DB table "templates" update/insert method for submit/unsubmit
# def submit_templates(template_id, submitted):
#     row = app_tables.templates.get(template_id=template_id)
#     if row is not None:
#         row['submitted'] = submitted
#         currenttime = datetime.now()
#         if submitted is True:
#             row['template_submitted'] = currenttime
  
# @anvil.server.callable
# # DB table "templates" delete method
# def delete_templates(template_id):
#     rows = app_tables.templates.search(template_id=template_id)
#     if len(list(rows)) != 0:
#         for r in rows:
#             r.delete()

# @anvil.server.callable
# # Random generate new template ID with 4 alphabets + 1 digit = 26^4 * 9 combinations if it is a new template
# # Otherwise return the selected template ID
# def get_template_id(templ_choice_str):
#     new_id = split_templ_id(templ_choice_str)
#     if (new_id == glo.input_stock_default_templ_dropdown()):
#         new_id = ''.join(random.choice(string.ascii_uppercase) for x in range(RANDOM_ID_ALPHA_LEN)) + str(random.randint(0,9))
#         while app_tables.templates.get(template_id=new_id) is not None:
#             new_id = ''.join(random.choice(string.ascii_uppercase) for x in range(RANDOM_ID_ALPHA_LEN)) + str(random.randint(0,9))
#         return new_id
#     else:
#         return new_id
  
# @anvil.server.callable
# # Update template name based on template dropdown selection
# def get_input_templ_name(templ_choice_str):
#     if templ_choice_str is None or templ_choice_str == '' or templ_choice_str == glo,input_stock_default_templ_dropdown():
#         return glo.input_stock_default_templ_name()
#     else:
#         row = app_tables.templates.get(template_id=split_templ_id(templ_choice_str))
#         return row['template_name'] if row is not None else glo.input_stock_default_templ_name()
  
# @anvil.server.callable
# # Return broker name based on template dropdown selection
# def get_input_templ_broker(templ_choice_str):
#     if templ_choice_str is None or templ_choice_str == '' or templ_choice_str == glo,input_stock_default_templ_dropdown():
#         row = cfmod.select_settings()
#         return row['default_broker'] if row is not None else ''
#     else:
#         row = app_tables.templates.get(template_id=split_templ_id(templ_choice_str))
#         return row['broker_id'] if row is not None else ''
    
# @anvil.server.callable
# # Generate DRAFTING template selection dropdown items
# def generate_template_dropdown():
#     #content = list(generate_template_dropdown_item(row['template_id'], row['template_name']) for row in app_tables.templates.search())
#     content = list(generate_template_dropdown_item(row['template_id'], row['template_name']) for row in app_tables.templates.search(submitted=False))
#     content.insert(0, glo.input_stock_default_templ_dropdown())
#     return content

# @anvil.server.callable
# # Generate SUBMITTED template selection dropdown items
# def get_submitted_templ_list():
#     #content = list(generate_template_dropdown_item(row['template_id'], row['template_name']) for row in app_tables.templates.search())
#     content = list(generate_template_dropdown_item(row['template_id'], row['template_name']) for row in app_tables.templates.search(submitted=True))
#     content.insert(0, '')
#     return content

# @anvil.server.callable
# # Return template items for repeating panel to display based on template selection dropdown
# def select_template_journals(templ_choice_str):
#     listitems = []
#     if not (templ_choice_str is None or templ_choice_str == glo.input_stock_default_templ_dropdown()):
#         listitems = list(app_tables.templ_journals.search(template_id=split_templ_id(templ_choice_str)))
#     return listitems

# @anvil.server.callable
# # DB table "templ_journals" select method
# def select_journals(end_date, start_date, symbols):
#     if len(symbols) > 0:
#         return app_tables.templ_journals.search(
#             q.all_of(sell_date=q.less_than_or_equal_to(end_date), 
#                      buy_date=q.greater_than_or_equal_to(start_date),
#                      symbol=q.any_of(*symbols)),
#             tables.order_by("sell_date", ascending=False),
#             tables.order_by("symbol", ascending=True),
#             )
#     else:
#         return app_tables.templ_journals.search(
#             q.all_of(sell_date=q.less_than_or_equal_to(end_date), 
#                      buy_date=q.greater_than_or_equal_to(start_date)),
#             tables.order_by("sell_date", ascending=False),
#             tables.order_by("symbol", ascending=True),
#             )

# @anvil.server.callable
# # Return template items for csv generation
# def generate_csv(end_date, start_date, symbols):
#     return select_journals(end_date, start_date, symbols).to_csv()

# @anvil.server.callable
# # Set precision
# def cal_profit(sell, buy, fee):
#     return round(float(sell) - float(buy) - float(fee), 2)

# @anvil.server.callable
# # Calculate stock sell/buy price
# def cal_price(amt, qty):
#     return round(float(amt) / float(qty), 2)

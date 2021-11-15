import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from . import mod_debug

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
# DB table "settings" update/insert method
def upsert_settings(def_ccy, def_interval, def_datefrom, def_dateto):
  rows = app_tables.settings.search()
  if len(list(rows)) != 0:
    for r in rows:
      r.delete()
  app_tables.settings.add_row(default_ccy=def_ccy, 
                              default_interval=def_interval, 
                              default_datefrom=def_datefrom,
                              default_dateto=def_dateto)

@anvil.server.callable
def select_settings():
  row = app_tables.settings.search()
  settings = {}
  for i in row:
    settings = {
      'default_ccy': i['default_ccy'],
      'default_interval': i['default_interval'],
      'default_datefrom': i['default_datefrom'],
      'default_dateto': i['default_dateto']
    }
  return settings

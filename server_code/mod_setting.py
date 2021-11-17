import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from . import mod_debug
from . import global_var

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
def upsert_settings(def_broker, def_interval, def_datefrom, def_dateto):
  rows = app_tables.settings.search()
  if len(list(rows)) != 0:
    for r in rows:
      r.delete()
  app_tables.settings.add_row(default_broker=def_broker, 
                              default_interval=def_interval, 
                              default_datefrom=def_datefrom,
                              default_dateto=def_dateto)

@anvil.server.callable
#
def select_settings():
  row = app_tables.settings.search()
  settings = {}
  for i in row:
    settings = {
      'default_broker': i['default_broker'],
      'default_interval': i['default_interval'],
      'default_datefrom': i['default_datefrom'],
      'default_dateto': i['default_dateto']
    }
  return settings

@anvil.server.callable
# DB table "brokers" select method
def select_brokers():
  #broker_list = global_var.setting_broker_dropdown() + \
  #              list((''.join([r['name'], ' [', r['ccy'], ']']), r['id']) for r in app_tables.brokers.search())
  #return broker_list
  return list((''.join([r['name'], ' [', r['ccy'], ']']), r['id']) for r in app_tables.brokers.search())

@anvil.server.callable
# DB table "brokers" update/insert method
def upsert_brokers(b_id, name, ccy):
  if b_id is None or b_id == '':
    # Generate new broker ID
    id_list = list(r['id'] for r in app_tables.brokers.search(tables.order_by('id', ascending=False)))
    if len(id_list) == 0:
      b_id = global_var.setting_broker_id_prefix() +  '1'.zfill(global_var.setting_broker_suffix_len())
    else:
      b_id = global_var.setting_broker_id_prefix() + str(int((id_list[:1][0])[2:]) + 1).zfill(global_var.setting_broker_suffix_len())
    app_tables.brokers.add_row(id=b_id, name=name, ccy=ccy)
  else:
    rows = app_tables.brokers.search(id=b_id)
    for r in rows:
      r.update(name=name, ccy=ccy)
  return b_id
      
@anvil.server.callable
# DB table "brokers" delete method
def delete_brokers(b_id):
  rows = app_tables.brokers.search(id=b_id)
  for r in rows:
    r.delete()
    
@anvil.server.callable
# Return selected broker name 
def get_broker_name(choice):
  result = app_tables.brokers.get(id=choice)
  return result['name'] if result is not None else ''
                   
@anvil.server.callable
# Return selected broker CCY 
def get_broker_ccy(choice):
  result = app_tables.brokers.get(id=choice)
  return result['ccy'] if result is not None else ''

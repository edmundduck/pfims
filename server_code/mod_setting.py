import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from . import mod_debug
from . import global_var
# PostgreSQL impl START
import psycopg2
import psycopg2.extras
# PostgreSQL impl END

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

# DB table "settings" select method from Anvil DB
def anvildb_select_settings():
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

# DB table "brokers" select method from Anvil DB
def anvildb_select_brokers():
  #broker_list = global_var.setting_broker_dropdown() + \
  #              list((''.join([r['name'], ' [', r['ccy'], ']']), r['id']) for r in app_tables.brokers.search())
  #return broker_list
  return list((''.join([r['name'], ' [', r['ccy'], ']']), r['id']) for r in app_tables.brokers.search())

# DB table "settings" update/insert method into Anvil DB
def anvildb_upsert_settings(def_broker, def_interval, def_datefrom, def_dateto):
  rows = app_tables.settings.search()
  if len(list(rows)) != 0:
    for r in rows:
      r.delete()
  app_tables.settings.add_row(default_broker=def_broker, 
                              default_interval=def_interval, 
                              default_datefrom=def_datefrom,
                              default_dateto=def_dateto)

# Return selected broker name from Anvil DB
def anvildb_get_broker_name(choice):
  result = app_tables.brokers.get(id=choice)
  return result['name'] if result is not None else ''

# Return selected broker CCY from Anvil DB
def anvildb_get_broker_ccy(choice):
  result = app_tables.brokers.get(id=choice)
  return result['ccy'] if result is not None else ''

# PostgreSQL impl START
# Establish PostgreSQL DB connection (Yugabyte DB)
def psqldb_connect():
  connection = psycopg2.connect(dbname='yugabyte',
                                host='europe-west2.793f25ab-3df2-4832-b84a-af6bdc81f2c7.gcp.ybdb.io',
                                port='5433',
                                user=anvil.secrets.get_secret('yugadb_app_usr'),
                                password=anvil.secrets.get_secret('yugadb_app_pw'))
  return connection

# DB table "settings" select method from PostgreSQL DB
def psqldb_select_settings():
  conn = psqldb_connect()
  with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
    cur.execute("SELECT default_broker, default_interval, default_datefrom, default_dateto FROM  " + global_var.db_schema_name() + ".settings")
    for i in cur.fetchall():
      settings = {
        'default_broker': i['default_broker'],
        'default_interval': i['default_interval'],
        'default_datefrom': i['default_datefrom'],
        'default_dateto': i['default_dateto']
      }
    cur.close()
  return settings

# DB table "brokers" select method from PostgreSQL DB
def psgldb_select_brokers():
  conn = psqldb_connect()
  with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
    cur.execute("SELECT id, name, ccy FROM  " + global_var.db_schema_name() + ".brokers ORDER BY id ASC")
    broker_list = cur.fetchall()
    cur.close()
  return list((''.join([r['name'], ' [', r['ccy'], ']']), r['id']) for r in broker_list)

# DB table "settings" update/insert method into PostgreSQL DB
def psgldb_upsert_settings(def_broker, def_interval, def_datefrom, def_dateto):
  conn = psqldb_connect()
  with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
    cur.execute("INSERT INTO " + global_var.db_schema_name() + ".settings \
    (app_uid, default_broker, default_interval, default_datefrom, default_dateto) \
    VALUES('" + anvil.users.get_user()['app_uid'] + "','" + def_broker + "','" + def_interval + "','" + str(def_datefrom) + "','" + str(def_dateto) + "') \
    ON CONFLICT (app_uid) DO UPDATE SET \
    default_broker='" + def_broker + "', default_interval='" + def_interval + \
    "', default_datefrom='" + str(def_datefrom) + "', default_dateto='" + str(def_dateto) + "'")
    count = cur.rowcount
    cur.close()
  return count

# Return selected broker name by querying DB table "brokers" from PostgreSQL DB
def psgldb_get_broker_name(choice):
  conn = psqldb_connect()
  with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
    cur.execute("SELECT name FROM " + global_var.db_schema_name() + ".brokers WHERE id='" + choice + "'")
    result = cur.fetchone()
  return result['name'] if result is not None else ''

# Return selected broker CCY by querying DB table "brokers" from PostgreSQL DB
def psgldb_get_broker_ccy(choice):
  conn = psqldb_connect()
  with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
    cur.execute("SELECT ccy FROM " + global_var.db_schema_name() + ".brokers WHERE id='" + choice + "'")
    result = cur.fetchone()
  return result['ccy'] if result is not None else ''

# PostgreSQL impl END

@anvil.server.callable
# DB table "settings" select method callable by client modules
def select_settings():
  return psqldb_select_settings()

@anvil.server.callable
# DB table "brokers" select method callable by client modules
def select_brokers():
  return psgldb_select_brokers()

@anvil.server.callable
# DB table "settings" update/insert method callable by client modules
def upsert_settings(def_broker, def_interval, def_datefrom, def_dateto):
  return psgldb_upsert_settings(def_broker, def_interval, def_datefrom, def_dateto)

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
# Return selected broker name callable by client modules
def get_broker_name(choice):
  return psgldb_get_broker_name(choice)

@anvil.server.callable
# Return selected broker CCY callable by client modules
def get_broker_ccy(choice):
  return psgldb_get_broker_ccy(choice)

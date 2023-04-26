import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import psycopg2
import psycopg2.extras

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.

@anvil.server.callable
# Get user logon name
def get_username(userid):
    row = app_tables.users.get_by_id(userid)
    print(dict(row))
    return row['email'] if row is not None else "" 

# Establish Postgres DB connection (Yugabyte DB)
def psqldb_connect():
    connection = psycopg2.connect(
        dbname='pfimsdb',
        host='europe-west2.793f25ab-3df2-4832-b84a-af6bdc81f2c7.gcp.ybdb.io',
        port='5433',
        user=anvil.secrets.get_secret('yugadb_app_usr'),
        password=anvil.secrets.get_secret('yugadb_app_pw'))
    return connection

# Return the DB FIN schema name
def schemafin():
  return "fin"

# Return the DB REFDATA schema name
def schemarefd():
  return "refdata"

# For debug print
def print_data_debug(message, debug_data):
    print('***[DEBUG]*** {}: {}'.format(message, debug_data))

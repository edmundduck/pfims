import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
# Postgres impl START
import psycopg2
import psycopg2.extras
# Postgres impl END

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

# Establish Postgres DB connection (Yugabyte DB)
def psqldb_connect():
    connection = psycopg2.connect(
        dbname='yugabyte',
        host='europe-west2.793f25ab-3df2-4832-b84a-af6bdc81f2c7.gcp.ybdb.io',
        port='5433',
        user=anvil.secrets.get_secret('yugadb_app_usr'),
        password=anvil.secrets.get_secret('yugadb_app_pw'))
    return connection

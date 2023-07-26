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

# Get user logon name
@anvil.server.callable
def get_current_username():
    userid = anvil.users.get_user().get_id()
    row = (app_tables.users.get_by_id(userid))['email']
    return row if row is not None else None

# Get user id (generated by Python)
@anvil.server.callable
def get_current_userid():
    userid = anvil.users.get_user().get_id()
    return userid[userid.find(",")+1:len(userid)-1] if type(userid) is str else None

# Get user logging level from server session, otherwise from DB table "settings"
@anvil.server.callable
def set_user_logging_level():
    if anvil.server.session is None or (anvil.server.session is not None and 'logging_level' not in anvil.server.session):
        conn = db_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(f"SELECT logging_level FROM {schemafin()}.settings WHERE userid='{get_current_userid()}'")
            result = cur.fetchone()
            anvil.server.session['logging_level'] = cur.fetchone().get('logging_level', None)
    return anvil.server.session.get('logging_level')

# Establish DB connection and determine which env DB to conntact to 
def db_connect():
    return psqldb_connect()
    
# Establish Postgres DB connection (Yugabyte DB)
def psqldb_connect():
    if anvil.app.environment.name in 'Dev':
        connection = psycopg2.connect(
            dbname=anvil.secrets.get_secret('devdb_name'),
            host=anvil.secrets.get_secret('devdb_host'),
            port=anvil.secrets.get_secret('devdb_port'),
            user=anvil.secrets.get_secret('devdb_app_usr'),
            password=anvil.secrets.get_secret('devdb_app_pw'))
    else:
        connection = psycopg2.connect(
            dbname=anvil.secrets.get_secret('proddb_name'),
            host=anvil.secrets.get_secret('proddb_host'),
            port=anvil.secrets.get_secret('proddb_port'),
            user=anvil.secrets.get_secret('proddb_app_usr'),
            password=anvil.secrets.get_secret('proddb_app_pw'))
    return connection

# Return the DB FIN schema name
def schemafin():
  return "fin"

# Return the DB REFDATA schema name
def schemarefd():
  return "refdata"

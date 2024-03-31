import anvil.files
from anvil.files import data_files
import anvil.server
import psycopg2
import psycopg2.extras
from .. import SystemProcess as sys

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.

@anvil.server.callable
def access_unit_test_data():
    conn = sys.db_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(open(data_files['load_unittest_data.sql']).read())
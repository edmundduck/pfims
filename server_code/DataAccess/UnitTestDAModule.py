import anvil.files
from anvil.files import data_files
import anvil.server
import psycopg2
import psycopg2.extras
from .. import SystemProcess as sys
from ..ServerUtils.LoggingModule import ServerLogger

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.
logger = ServerLogger()

@anvil.server.callable
def initialize_unit_test_data():
    """
    Initialize data for unit test by loading data from script.
    """
    conn = sys.db_connect()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(open(data_files['load_unittest_data.sql']).read())
            conn.commit()
    except psycopg2.OperationalError as err:
        logger.error(err)
        conn.rollback()
        raise psycopg2.OperationalError(err)
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()        

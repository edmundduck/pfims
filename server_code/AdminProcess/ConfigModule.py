import anvil.files
from anvil.files import data_files
import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import psycopg2
import psycopg2.extras
from ..InvestmentProcess import InputModule
from ..ServerUtils import HelperModule as helper
from ..SysProcess import Constants as s_const
from ..SysProcess import SystemModule as sysmod
from ..SysProcess import LoggingModule
from ..CashMgtProcess import AccountModule
from ..Entities.Setting import Setting

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.
logger = LoggingModule.ServerLogger()

@anvil.server.callable('select_settings', require_user=True)
@logger.log_function
def select_settings():
    """
    Select user's settings from the user's setting DB table.

    Returns:
        setting (Setting): Setting object contains all user's setting.
    """
    def psqldb_select_settings():
        userid = sysmod.get_current_userid()
        conn = sysmod.db_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            sql = "SELECT default_broker, default_interval, default_datefrom, default_dateto, logging_level FROM {schema}.settings WHERE userid=%s".format(schema=sysmod.schemafin())
            stmt = cur.mogrify(sql, (userid, ))
            cur.execute(stmt)
            row = cur.fetchone()
            logger.debug("settings=", row)
            cur.close()
        return row

    setting = Setting(psqldb_select_settings())
    return setting

@anvil.server.callable('generate_brokers_simplified_list')
@logger.log_function
def generate_brokers_simplified_list():
    """
    Select part of investment broker's data from the broker DB table.

    Returns:
        broker_dropdown (list): A dropdown list of broker names and CCY as description, and broker ID as ID.
    """
    def psgldb_generate_brokers_simplified_list():
        userid = sysmod.get_current_userid()
        conn = sysmod.db_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            sql = "SELECT broker_id, name, ccy FROM {schema}.brokers WHERE userid = {userid} ORDER BY broker_id ASC".format(schema=sysmod.schemafin(), userid=userid)
            cur.execute(sql)
            rows = cur.fetchall()
            logger.debug("simplified_list=", rows)
            cur.close()
        # broker_dropdown = list((''.join([r['name'], ' [', r['ccy'], ']']), (r['broker_id'], r['name'], r['ccy'])) for r in result)
        return rows

    return psgldb_generate_brokers_simplified_list()

@anvil.server.callable('upsert_settings', require_user=True)
@logger.log_function
def upsert_settings(setting):
    """
    Insert or update settings from setting form to a DB table which stores user's settings detail.

    Row count returned larger than 0 is considered as a successful update. At the same time, logging level is updated into the server user session.
    
    Parameters:
        def_broker (str): The name of the broker.
        def_interval (str): The ID of the default search interval.
        def_datefrom (date): The date to default search from.
        def_dateto (date): The date to default search to.
        logging_level (int): The user's logging level mostly based on Python's logging module, data type in DB is smallint.

    Returns:
        int: Successful update row count, otherwise None
    """
    def psgldb_upsert_settings():
        conn, cur = None * 2
        try:
            if isinstance(setting, Setting):
                userid = setting.get_userid()
                if sysmod.get_current_userid() != userid:
                    raise RuntimeError(f"Unauthorized access to other's user settings.")
                if def_interval != s_const.SearchInterval.INTERVAL_SELF_DEFINED: def_datefrom, def_dateto = [None, None]
                conn = sysmod.db_connect()
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                    sql = f"INSERT INTO {sysmod.schemafin()}.settings (userid, default_broker, default_interval, default_datefrom, \
                    default_dateto, logging_level) VALUES (%s,%s,%s,%s,%s,%s) ON CONFLICT (userid) DO UPDATE SET default_broker=%s, \
                    default_interval=%s, default_datefrom=%s, default_dateto=%s, logging_level=%s"
                    stmt = cur.mogrify(sql, (userid, def_broker, def_interval, def_datefrom, def_dateto, logging_level, def_broker, def_interval, def_datefrom, def_dateto, logging_level))
                    cur.execute(stmt)
                    conn.commit()
                    logger.debug(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
                    if cur.rowcount <= 0: raise psycopg2.OperationalError("Update settings fail with rowcount <= 0.")
                    anvil.server.session['loglevel'] = logging_level
                    return cur.rowcount
            else:
                raise TypeError(f"The parameter is not a Setting object.")
        except (RuntimeError, TypeError) as err:
            logger.error(err)
        except psycopg2.OperationalError as err:
            logger.error(err)
            conn.rollback()
        finally:
            if cur is not None: cur.close()
            if conn is not None: conn.close()
        return None

    return psgldb_upsert_settings(def_broker, def_interval, def_datefrom, def_dateto, logging_level)

@logger.log_function
def psgldb_upsert_brokers(b_id, prefix, name, ccy):
    """
    Insert or update an investment broker from setting form to the DB table which stores investment brokers' detail.

    Row count returned larger than 0 is considered as a successful update. At the same time, logging level is updated into the server user session.
    
    Parameters:
        b_id (str): The ID of the broker.
        prefix (str): The prefix of the broker ID.
        name (str): The name of the broker.
        ccy (str): The base CCY of the broker.

    Returns:
        b_id (int): The ID of the newly created or existing broker, otherwise None
    """
    userid = sysmod.get_current_userid()
    try:
        conn = sysmod.db_connect()  
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            if b_id in (None, ''):
                cur.execute(f"INSERT INTO {sysmod.schemafin()}.brokers (userid, prefix, name, ccy) VALUES ({userid},'{prefix}','{name}','{ccy}') RETURNING id")
                # broker_id (update by rule) is not updated right after INSERT INTO above, hence cannot obtain using RETURNING phrase
                id = cur.fetchone()['id']
                conn.commit()
                cur.execute(f"SELECT broker_id FROM {sysmod.schemafin()}.brokers WHERE id={str(id)}")
                b_id = cur.fetchone()['broker_id']
            else:
                cur.execute(f"UPDATE {sysmod.schemafin()}.brokers SET prefix='{prefix}', name='{name}', ccy='{ccy}' WHERE broker_id='{b_id}'")
                conn.commit()
                if cur.rowcount <= 0: raise psycopg2.OperationalError("Update broker fail with rowcount <= 0.")
            logger.debug(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
            return b_id
    except (Exception, psycopg2.OperationalError) as err:
        logger.error(err)
        conn.rollback()
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()
    return None
      
@logger.log_function
def psgldb_delete_brokers(b_id):
    """
    Delete an investment broker from the DB table which stores investment brokers' detail.

    Row count returned larger than 0 is considered as a successful update.
    
    Parameters:
        b_id (str): The ID of the broker.

    Returns:
        cur.rowcount (int): Successful update row count, otherwise None.
    """
    try:
        conn = sysmod.db_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(f"DELETE FROM {sysmod.schemafin()}.brokers WHERE broker_id = '{b_id}'")
            conn.commit()
            logger.debug(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
            if cur.rowcount <= 0: raise psycopg2.OperationalError("Delete brokers fail with rowcount <= 0.")
            return cur.rowcount
    except (Exception, psycopg2.OperationalError) as err:
        logger.error(err)
        conn.rollback()
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()
    return None

@anvil.server.callable("psgldb_get_submitted_templ_list")
@logger.log_function
def psgldb_get_submitted_templ_list():
    """
    Select "Submitted" templates from the DB table which stores templates' detail to generate a dropdown list.

    Returns:
        result (list): A dropdown list of submitted template names as description, and submitted template IDs as ID.
    """
    userid = sysmod.get_current_userid()
    conn = sysmod.db_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(f"SELECT template_id, template_name FROM {sysmod.schemafin()}.templates WHERE userid = {userid} AND submitted=true")
        result = list((''.join([row['template_name'], ' [', str(row['template_id']), ']']), (row['template_id'], row['template_name'])) for row in cur.fetchall())
        logger.debug("result=", result)
        cur.close()
    return result
        
@logger.log_function
def psgldb_select_search_interval():
    """
    Select data from a DB table which stores search intervals' detail to generate a dropdown list.

    Returns:
        list: A dropdown list of search interval name as description, and search interval ID as ID.
    """
    conn = sysmod.db_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(f"SELECT * FROM {sysmod.schemarefd()}.search_interval ORDER BY seq ASC")
        rows = cur.fetchall()
        logger.debug("rows=", rows)
        cur.close()
    return list((row['name'], row['id']) for row in rows)

@anvil.server.callable
def upsert_brokers(b_id, name, ccy):
    """
    A wrapper function to insert or update brokers detail.

    The prefix of a broker ID is currently predefined in a constant file and used here.
    
    Parameters:
        b_id (str): The ID of the broker.
        name (str): The name of the broker.
        ccy (str): The base CCY of the broker.

    Returns:
        function: A function to actual execute the logic in DB.
    """
    return psgldb_upsert_brokers(b_id, s_const.SettingConfig.BROKER_ID_PREFIX, name, ccy)
      
@anvil.server.callable
def delete_brokers(b_id):
    """
    A wrapper function to delete brokers detail.

    Parameters:
        b_id (str): The ID of the broker.

    Returns:
        function: A function to actual execute the logic in DB.
    """
    return psgldb_delete_brokers(b_id)
    
@anvil.server.callable
# Generate SUBMITTED template selection dropdown items
def get_submitted_templ_list():
    """
    A wrapper function to select submitted templates to generate a dropdown list.

    Returns:
        function: A function to actual execute the logic in DB.
    """
    return psgldb_get_submitted_templ_list()

@anvil.server.callable
# DB table "search_interval" select method callable by client modules
def select_search_interval():
    """
    A wrapper function to select search interval to generate a dropdown list.

    Returns:
        function: A function to actual execute the logic in DB.
    """
    return psgldb_select_search_interval()

@anvil.server.callable("proc_init_settings")
@logger.log_function
def proc_init_settings():
    """
    Consolidated process for setting form initialization.

    Returns:
        list: A list of all functions return required by the form initialization.
    """
    settings = select_settings()
    search_interval = select_search_interval()
    ccy = AccountModule.generate_ccy_dropdown()
    submitted_templ_list = get_submitted_templ_list()
    return [settings, search_interval, ccy, submitted_templ_list]

@anvil.server.callable("proc_upsert_settings")
@logger.log_function
def proc_upsert_settings(def_broker, def_interval, def_datefrom, def_dateto, logging_level):
    """
    Consolidated process for settings update.

    Parameters:
        def_broker (str): The name of the broker.
        def_interval (str): The ID of the default search interval.
        def_datefrom (date): The date to default search from.
        def_dateto (date): The date to default search to.
        logging_level (int): The user's logging level mostly based on Python's logging module, data type in DB is smallint.

    Returns:
        int: Successful update row count, otherwise None
    """
    count = upsert_settings(def_broker, def_interval, def_datefrom, def_dateto, logging_level)
    sysmod.set_user_logging_level()
    return count

@anvil.server.callable("proc_broker_create_update")
@logger.log_function
def proc_broker_create_update(b_id, name, ccy):
    """
    Consolidated process for broker creation and update.

    Returns:
        list: A list of all functions return required by the broker creation and update.
    """
    broker_id = upsert_brokers(b_id, name, ccy)
    return [broker_id, None]

@anvil.server.callable("proc_broker_delete")
@logger.log_function
def proc_broker_delete(b_id):
    """
    Consolidated process for broker deletion.

    Returns:
        list: A list of all functions return required by the broker deletion.
    """
    count = delete_brokers(b_id)
    return [count, None]

@anvil.server.callable("proc_submitted_template_update")
@logger.log_function
def proc_submitted_template_update(templ_id):
    """
    Consolidated process for submitted template dropdown update.

    Parameters:
        templ_id (int): ID of the template.

    Returns:
        list: A list of all functions return required by the submitted template dropdown update.
    """
    result = InputModule.submit_templates(templ_id, False)

    if result is not None and result > 0:
        submitted_templ_list = get_submitted_templ_list()
        return [templ_id, result, submitted_templ_list]
    else:
        return [templ_id, result, None]

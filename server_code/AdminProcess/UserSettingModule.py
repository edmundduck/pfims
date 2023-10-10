import anvil.users
import anvil.server
import psycopg2
import psycopg2.extras
from ..Entities.Setting import Setting
from ..InvestmentProcess import InputModule
from ..SysProcess import SystemModule as sysmod
from ..SysProcess import LoggingModule
from ..Utils.Constants import SettingConfig

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
            sql = "SELECT userid, default_broker, default_interval, default_datefrom, default_dateto, logging_level FROM {schema}.settings WHERE userid=%s".format(schema=sysmod.schemafin())
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
        rows (list of RealDictRow): A list consists of broker IDs, names and CCY as description.
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
        cur.rowcount (int): Successful update row count, otherwise None
    """
    def psgldb_upsert_settings():
        conn, cur = [None]*2
        try:
            if isinstance(setting, Setting):
                setting.userid = sysmod.get_current_userid()
                mogstr = setting.get_list() + setting.get_list()[1:]
                logging_level = mogstr[-1]
                conn = sysmod.db_connect()
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                    sql = f"INSERT INTO {sysmod.schemafin()}.settings (userid, default_broker, default_interval, default_datefrom, \
                    default_dateto, logging_level) VALUES (%s,%s,%s,%s,%s,%s) ON CONFLICT (userid) DO UPDATE SET default_broker=%s, \
                    default_interval=%s, default_datefrom=%s, default_dateto=%s, logging_level=%s"
                    stmt = cur.mogrify(sql, mogstr)
                    cur.execute(stmt)
                    conn.commit()
                    logger.debug(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
                    if cur.rowcount <= 0: raise psycopg2.OperationalError("Update settings fail with rowcount <= 0.")
                    anvil.server.session['loglevel'] = logging_level
                    return cur.rowcount
            else:
                raise TypeError(f"The parameter is not a Setting object.")
        except TypeError as err:
            logger.error(err)
        except psycopg2.OperationalError as err:
            logger.error(err)
            conn.rollback()
        finally:
            if cur is not None: cur.close()
            if conn is not None: conn.close()
        return None

    return psgldb_upsert_settings()

@anvil.server.callable('create_broker')
@logger.log_function
def create_broker(broker_name, ccy):
    """
    Create an investment broker and save the change into the brokers DB table.

    Parameters:
        broker_name (str): The name of the broker.
        ccy (str): The base CCY of the broker.

    Returns:
        broker_id (int): The ID of the newly created broker, otherwise None
    """
    def psgldb_create_broker():
        userid = sysmod.get_current_userid()
        prefix = SettingConfig.BROKER_ID_PREFIX
        try:
            conn = sysmod.db_connect()  
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(f"INSERT INTO {sysmod.schemafin()}.brokers (userid, prefix, name, ccy) VALUES ({userid},'{prefix}','{broker_name}','{ccy}') RETURNING id")
                # broker_id (update by rule) is not updated right after INSERT INTO above, hence cannot obtain using RETURNING phrase
                id = cur.fetchone()['id']
                conn.commit()
                cur.execute(f"SELECT broker_id FROM {sysmod.schemafin()}.brokers WHERE id={id}")
                broker_id = cur.fetchone()['broker_id']
                if id <= 0 and broker_id is None: raise psycopg2.OperationalError("Create broker fail with invalid broker ID.")
                logger.debug(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
                return broker_id
        except psycopg2.OperationalError as err:
            logger.error(err)
            conn.rollback()
        finally:
            if cur is not None: cur.close()
            if conn is not None: conn.close()
        return None
    return psgldb_create_broker()
      
@anvil.server.callable('update_broker')
@logger.log_function
def update_broker(broker_id, broker_name, ccy):
    """
    Update an investment broker and save the change into the brokers DB table.

    Parameters:
        broker_id (str): The ID of the broker.
        broker_name (str): The name of the broker.
        ccy (str): The base CCY of the broker.

    Returns:
        cur.rowcount (int): Successful update row count, otherwise None
    """
    def psgldb_update_broker():
        userid = sysmod.get_current_userid()
        prefix = SettingConfig.BROKER_ID_PREFIX
        try:
            conn = sysmod.db_connect()  
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(f"UPDATE {sysmod.schemafin()}.brokers SET prefix='{prefix}', name='{broker_name}', ccy='{ccy}' WHERE broker_id='{broker_id}'")
                conn.commit()
                logger.debug(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
                if cur.rowcount <= 0: raise psycopg2.OperationalError("Update broker fail with rowcount <= 0.")
                return cur.rowcount
        except psycopg2.OperationalError as err:
            logger.error(err)
            conn.rollback()
        finally:
            if cur is not None: cur.close()
            if conn is not None: conn.close()
        return None
    return psgldb_update_broker()

@anvil.server.callable('delete_broker')
@logger.log_function
def delete_broker(broker_id):
    """
    Delete an investment broker and save the change into the brokers DB table.

    Row count returned larger than 0 is considered as a successful update.
    
    Parameters:
        broker_id (str): The ID of the broker.

    Returns:
        cur.rowcount (int): Successful update row count, otherwise None.
    """
    def psgldb_delete_broker():
        try:
            conn = sysmod.db_connect()
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(f"DELETE FROM {sysmod.schemafin()}.brokers WHERE broker_id = '{broker_id}'")
                conn.commit()
                logger.debug(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
                if cur.rowcount <= 0: raise psycopg2.OperationalError("Delete brokers fail with rowcount <= 0.")
                return cur.rowcount
        except psycopg2.OperationalError as err:
            logger.error(err)
            conn.rollback()
        finally:
            if cur is not None: cur.close()
            if conn is not None: conn.close()
        return None
    return psgldb_delete_broker()
    
@anvil.server.callable("generate_currency_list")
@logger.log_function
def generate_currency_list():
    """
    Select refence data - Currency (CCY)  from the currency DB table.

    Note that not all currencies have symbols, they can be empty.

    Returns:
        rows (list of RealDictRow): A list consists of CCY names, abbreviations and symbols.
    """
    conn = sysmod.db_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(f"SELECT * FROM {sysmod.schemarefd()}.ccy ORDER BY common_seq ASC, abbv ASC")
        rows = cur.fetchall()
        logger.trace("rows=", rows)
        cur.close()
    return rows

@anvil.server.callable("generate_submitted_journal_groups_list")
@logger.log_function
def generate_submitted_journal_groups_list():
    """
    Select "Submitted" journal groups from the stock journal groups DB table.

    Returns:
        rows (list of RealDictRow): A list consists of submitted journal groups IDs and names.
    """
    def psgldb_generate_submitted_journal_groups_list():
        userid = sysmod.get_current_userid()
        conn = sysmod.db_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(f"SELECT template_id, template_name FROM {sysmod.schemafin()}.templates WHERE userid = {userid} AND submitted=true")
            rows = cur.fetchall()
            logger.debug("rows=", rows)
            cur.close()
        return rows
    return psgldb_generate_submitted_journal_groups_list()

@anvil.server.callable('generate_search_interval_list')
@logger.log_function
def generate_search_interval_list():
    """
    Select reference data - search interval from the search interval DB table.

    Returns:
        rows (list of RealDictRow): A list consists of search interval ID and name.
    """
    def psgldb_generate_search_interval_list():
        conn = sysmod.db_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(f"SELECT id, name FROM {sysmod.schemarefd()}.search_interval ORDER BY seq ASC")
            rows = cur.fetchall()
            logger.debug("rows=", rows)
            cur.close()
        return rows
    return psgldb_generate_search_interval_list()

@anvil.server.callable("proc_init_settings")
@logger.log_function
def proc_init_settings():
    """
    Consolidated process for setting form initialization.

    Returns:
        list: A list of all functions return required by the form initialization.
    """
    settings = select_settings()
    brokers = generate_brokers_simplified_list()
    search_interval = generate_search_interval_list()
    ccy = generate_currency_list()
    submitted_group_list = generate_submitted_journal_groups_list()
    return [settings, brokers, search_interval, ccy, submitted_group_list]

@anvil.server.callable("proc_upsert_settings")
@logger.log_function
def proc_upsert_settings(setting):
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
    count = upsert_settings(setting)
    sysmod.set_user_logging_level()
    return count

@anvil.server.callable("proc_submitted_journal_group_update")
@logger.log_function
def proc_submitted_journal_group_update(templ_id):
    """
    Consolidated process for submitted template dropdown update.

    Parameters:
        templ_id (int): ID of the template.

    Returns:
        result (int): Successful submit row count, otherwise None.
    """
    result = InputModule.submit_templates(templ_id, False)
    return result

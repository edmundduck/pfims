import anvil.server
import psycopg2
import psycopg2.extras
from datetime import date, datetime
from ..Entities.StockJournalGroup import StockJournalGroup
from ..Entities.StockJournal import StockJournal
from ..DataObject import FinObject as fobj
from ..SysProcess import SystemModule as sysmod
from ..SysProcess import LoggingModule
from ..Utils.Constants import Database

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.
logger = LoggingModule.ServerLogger()

@anvil.server.callable("generate_drafting_stock_journal_groups_list")
@logger.log_function
def generate_drafting_stock_journal_groups_list():
    """
    Select DRAFTING (a.k.a. unsubmitted) stock journal groups from the template DB table.

    Returns:
        rows (list of RealDictRow): A list of unsubmitted template item formed by template IDs and names.
    """
    userid = sysmod.get_current_userid()
    conn = sysmod.db_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        sql = 'SELECT * FROM {schema}.templates WHERE userid = {userid} AND submitted=false ORDER BY template_id ASC'.format(
            schema=Database.SCHEMA_FIN,
            userid=userid
        )
        cur.execute(sql)
        rows = cur.fetchall()
        logger.trace("rows=", rows)
        cur.close()
        return rows

@anvil.server.callable("select_stock_journal_group")
@logger.log_function
def select_stock_journal_group(group_id):
    """
    Return selected stock journal group detail.
    
    Parameters:
        group_id (int): ID of the stock journal group.

    Returns:
        jrn_grp (StockJournalGroup): A stock journal group object.
    """
    conn = sysmod.db_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        sql = 'SELECT {col_def} FROM {schema}.templates WHERE template_id=%s'.format(
            col_def=StockJournalGroup.get_column_definition(),
            schema=Database.SCHEMA_FIN
        )
        stmt = cur.mogrify(sql, (group_id, ))
        cur.execute(stmt)
        row = cur.fetchone()
        logger.trace('row=', row)
        cur.close()
        return StockJournalGroup(row)
  
@anvil.server.callable("select_stock_journals")
@logger.log_function
def select_stock_journals(group_id):
    """
    Return all journals under a selected stock journal group.

    Parameters:
        group_id (int): ID of the stock journal group.

    Returns:
        jrns (list of StockJournal): All journals detail corresponding to the selected stock journal group, return empty list otherwise
    """
    userid = sysmod.get_current_userid()
    conn = sysmod.db_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        sql = 'SELECT * FROM {schema}.templ_journals WHERE template_id = %s ORDER BY sell_date DESC, buy_date DESC, symbol ASC'.format(
            schema=Database.SCHEMA_FIN
        )
        stmt = cur.mogrify(sql, (group_id, ))
        cur.execute(stmt)
        rows = cur.fetchall()
        logger.trace('rows=', rows)
        cur.close()
        jrns = list(StockJournal(r).set_user_id(userid) for r in rows)
        return jrns

@anvil.server.callable("upsert_journals")
@logger.log_function
def upsert_journals(jrn_grp):
    """
    Insert or update journals into the DB table which stores template journals.

    Column IID is not generated in application side, it's handled by DB function instead, 
    hence running SQL scripts in DB is required beforehand.
    
    Parameters:
        jrn_grp (StockJournalGroup): The StockJournalGroup object of the selected stock journal group.

    Returns:
        cur.rowcount (int): Successful update row count, otherwise None.
    """
    try:
        cur, conn = [None]*2
        if isinstance(jrn_grp, StockJournalGroup):
            conn = sysmod.db_connect() 
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                # Reference for solving the SQL mogrify with multiple groups and update on conflict problems
                # 1. https://www.geeksforgeeks.org/format-sql-in-python-with-psycopgs-mogrify/
                # 2. https://dba.stackexchange.com/questions/161127/column-reference-is-ambiguous-when-upserting-element-into-table
                if len(jrn_grp.get_journals()) > 0:
                    mogstr = []
                    for r in jrn_grp.get_journals():
                        print(r)
                    mogstr.append(cur.mogrify("(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", r.get_list()).decode('utf-8') for r in jrn_grp.get_journals())
                    logger.trace("mogstr=", mogstr)
                    sql = 'INSERT INTO {schema}.templ_journals (iid, template_id, sell_date, buy_date, symbol, qty, sales, cost, fee, sell_price, buy_price, pnl) \
                    VALUES {p1} ON CONFLICT (iid, template_id) DO UPDATE SET sell_date=EXCLUDED.sell_date, buy_date=EXCLUDED.buy_date, symbol=EXCLUDED.symbol, \
                    qty=EXCLUDED.qty, sales=EXCLUDED.sales, cost=EXCLUDED.cost, fee=EXCLUDED.fee, sell_price=EXCLUDED.sell_price, buy_price=EXCLUDED.buy_price, \
                    pnl=EXCLUDED.pnl WHERE templ_journals.iid=EXCLUDED.iid AND templ_journals.template_id=EXCLUDED.template_id'.format(
                            schema=Database.SCHEMA_FIN,
                            p1=','.join(mogstr)
                        )
                    cur.execute(sql)
                    conn.commit()
                    logger.debug(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
                    if cur.rowcount <= 0: raise psycopg2.OperationalError(f'Stock journals in group=[{jrn_grp.get_name()} ({jrn_grp.get_id()})] insert or update fail.')
                    return cur.rowcount
                return 0
        raise TypeError('The parameter is not a StockJournalGroup object.')
    except psycopg2.OperationalError as err:
        logger.error(err)
        conn.rollback()
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()
    return None
    
@anvil.server.callable("delete_journals")
@logger.log_function
def delete_journals(jrn_grp, iid_list):
    """
    Delete journals from the DB table which stores template journals.

    Parameters:
        jrn_grp (StockJournalGroup): The StockJournalGroup object of the selected stock journal group.
        iid_list (list): The list of IID requiring deletion.

    Returns:
        cur.rowcount (int): Successful delete row count, otherwise None.
    """
    try:
        cur, conn = [None]*2
        if isinstance(jrn_grp, StockJournalGroup):
            if iid_list and len(iid_list) > 0:
                conn = sysmod.db_connect()
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                    sql = "DELETE FROM {schema}.templ_journals WHERE template_id = %s AND iid IN %s".format(
                        schema=Database.SCHEMA_FIN,
                    )
                    stmt = cur.mogrify(sql, (jrn_grp.get_id(), tuple(iid_list)))
                    cur.execute(stmt)
                    conn.commit()
                    logger.debug(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
                    if cur.rowcount <= 0: raise psycopg2.OperationalError(f'Stock journals in group=[{jrn_grp.get_name()} ({jrn_grp.get_id()})] deletion fail, iid to be deleted=[{iid_list}]')
                    return cur.rowcount
            return 0
        raise TypeError('The parameter is not a StockJournalGroup object.')
    except psycopg2.OperationalError as err:
        logger.error(err)
        conn.rollback()
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()
    return None

@anvil.server.callable("save_new_stock_journal_group")
@logger.log_function
def save_new_stock_journal_group(jrn_grp):
    """
    Save a new stock journal group into the stock journal group DB table.

    Parameters:
        jrn_grp (StockJournalGroup): The StockJournalGroup object of the selected stock journal group.

    Returns:
        tid['template_id'] (int): Template ID if save is successful, otherwise None.
    """
    try:
        cur, conn = [None]*2
        if isinstance(jrn_grp, StockJournalGroup):
            userid = sysmod.get_current_userid()
            conn = sysmod.db_connect()
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                sql = "INSERT INTO {schema}.templates (userid, template_name, broker_id, submitted, template_create, template_lastsave) \
                VALUES (%s,%s,%s,%s,%s,%s) RETURNING template_id".format(
                    schema=Database.SCHEMA_FIN
                )
                mogstr = [userid, jrn_grp.get_name(), jrn_grp.get_broker(), jrn_grp.get_submitted_status(), \
                        jrn_grp.get_created_time(), jrn_grp.get_lastsaved_time()]
                stmt = cur.mogrify(sql, mogstr)
                cur.execute(stmt)
                conn.commit()
                logger.debug(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
                tid = cur.fetchone()
                logger.debug("tid=", tid)
                if not tid or tid.get('template_id', -1) < 0: 
                    raise psycopg2.OperationalError(f'Stock journal group [{jrn_grp.get_name()}] creation fail.')
                return tid.get('template_id', -1)
        raise TypeError('The parameter is not a StockJournalGroup object.')
    except psycopg2.OperationalError as err:
        logger.error(err)
        conn.rollback()
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()
    return None

@anvil.server.callable("save_existing_stock_journal_group")
@logger.log_function
def save_existing_stock_journal_group(jrn_grp):
    """
    Save existing stock journal group change into the stock journal group DB table.

    Parameters:
        jrn_grp (StockJournalGroup): The StockJournalGroup object of the selected stock journal group.

    Returns:
        tid['template_id'] (int): Template ID if save is successful, otherwise None.
    """
    try:
        cur, conn = [None]*2
        if isinstance(jrn_grp, StockJournalGroup):
            userid = sysmod.get_current_userid()
            currenttime = datetime.now()
            conn = sysmod.db_connect()
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                sql = "UPDATE {schema}.templates SET template_name = %s, broker_id = %s, submitted = %s, template_lastsave = %s WHERE template_id = %s RETURNING template_id".format(
                    schema=Database.SCHEMA_FIN
                )
                mogstr = [jrn_grp.get_name(), jrn_grp.get_broker(), jrn_grp.get_submitted_status(), jrn_grp.get_lastsaved_time(), jrn_grp.get_id()]
                stmt = cur.mogrify(sql, mogstr)
                cur.execute(stmt)
                conn.commit()
                logger.debug(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
                tid = cur.fetchone()
                logger.debug("tid=", tid)
                if not tid or tid.get('template_id', -1) < 0: 
                    raise psycopg2.OperationalError(f'Stock journal group [{jrn_grp.get_name()} ({jrn_grp.get_id()})] update fail.')
                return tid['template_id']
        raise TypeError('The parameter is not a StockJournalGroup object.')
    except psycopg2.OperationalError as err:
        logger.error(err)
        conn.rollback()
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()
    return None

@anvil.server.callable("submit_stock_journal_group")
@logger.log_function
def submit_stock_journal_group(jrn_grp):
    """
    Submit a new stock journal group to change this group to be either editable (unsubmitted) or not editable (submitted).

    Parameters:
        jrn_grp (StockJournalGroup): The StockJournalGroup object of the selected stock journal group.

    Returns:
        cur.rowcount (int): Successful submit row count, otherwise None.
    """
    try:
        cur, conn = [None]*2
        if isinstance(jrn_grp, StockJournalGroup):
            currenttime = datetime.now()
            conn = sysmod.db_connect()
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                submitted = jrn_grp.get_submitted_status()
                if submitted:
                    sql = "UPDATE {schema}.templates SET submitted = %s, template_submitted = %s WHERE template_id = %s".format(
                        schema=Database.SCHEMA_FIN
                    )
                    mogstr = [submitted, jrn_grp.get_submitted_time(), jrn_grp.get_id()]
                else:
                    sql = "UPDATE {schema}.templates SET submitted = %s WHERE template_id = %s".format(
                        schema=Database.SCHEMA_FIN
                    )
                    mogstr = [submitted, jrn_grp.get_id()]
                stmt = cur.mogrify(sql, mogstr)
                cur.execute(stmt)
                conn.commit()
                logger.debug(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
                if cur.rowcount <= 0: raise psycopg2.OperationalError(f'Stock journal group [{jrn_grp.get_name()} ({jrn_grp.get_id()})] submission or reversal fail.')
                return cur.rowcount
        raise TypeError('The parameter is not a StockJournalGroup object.')
    except psycopg2.OperationalError as err:
        logger.error(err)
        conn.rollback()
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()
    return None
  
@anvil.server.callable("delete_stock_journal_group")
@logger.log_function
def delete_stock_journal_group(jrn_grp):
    """
    Delete a new stock journal group from the stock journal group DB table.
    
    Delete cascade is implemented in the DB table (which stores stock journal group journals detail) "template_id" column, 
    hence journals under particular group will be deleted automatically.

    Parameters:
        jrn_grp (StockJournalGroup): The StockJournalGroup object of the selected stock journal group.

    Returns:
        cur.rowcount (int): Successful delete row count, otherwise None.
    """
    try:
        cur, conn = [None]*2
        if isinstance(jrn_grp, StockJournalGroup):
            conn = sysmod.db_connect()
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                sql = 'DELETE FROM {schema}.templates WHERE template_id = %s'.format(schema=Database.SCHEMA_FIN)
                stmt = cur.mogrify(sql, (jrn_grp.get_id(), ))
                cur.execute(stmt)
                conn.commit()
                logger.debug(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
                if cur.rowcount <= 0: raise psycopg2.OperationalError(f'Stock journal group [{jrn_grp.get_name()} ({jrn_grp.get_id()})] deletion fail.')
                return cur.rowcount
        raise TypeError('The parameter is not a StockJournalGroup object.')
    except psycopg2.OperationalError as err:
        logger.error(err)
        conn.rollback()
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()
    return None

@anvil.server.callable("proc_save_group_and_journals")
@logger.log_function
def proc_save_group_and_journals(jrn_grp, del_iid_list=None):
    """
    Consolidated process for saving stock journal group and journals.

    Parameters:
        jrn_grp (StockJournalGroup): The StockJournalGroup object of the selected stock journal group.
        del_iid_list (list): A list of IID (item ID) to be deleted, every journal has an IID.

    Returns:
        jrn_grp (StockJournalGroup): The StockJournalGroup object of the selected stock journal group.
        result_u (int): Successful update row count, otherwise None.
        result_d (int): Successful delete row count, otherwise None.
    """
    result_d = delete_journals(jrn_grp, del_iid_list)
    if jrn_grp.get_id():
        group_id = save_existing_stock_journal_group(jrn_grp)
    else:
        group_id = save_new_stock_journal_group(jrn_grp)
        if group_id is None or group_id <= 0:
            raise RuntimeError(f'ERROR: Fail to create new stock journal group {group_name}, aborting further update on journals.')
        jrn_grp = jrn_grp.set_id(group_id)
    result_u = upsert_journals(jrn_grp)
    return [jrn_grp, result_u, result_d]

@anvil.server.callable("init_cache_stock_trading_txn_detail")
@logger.log_function
def init_cache_stock_trading_txn_detail():
    from ..AdminProcess import UserSettingModule
    broker_list = UserSettingModule.generate_brokers_simplified_list()
    jrn_list = generate_drafting_stock_journal_groups_list()
    return [broker_list, jrn_list]
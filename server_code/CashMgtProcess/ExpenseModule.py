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
from datetime import date, datetime
from ..DataObject.FinObject import ExpenseRecord as exprcd
from ..ServerUtils import HelperModule as helper
from ..SysProcess import SystemModule as sysmod
from ..SysProcess import LoggingModule
from ..Utils.Constants import Database

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.
logger = LoggingModule.ServerLogger()

@anvil.server.callable("generate_expensetabs_dropdown")
@logger.log_function
def generate_expensetabs_dropdown():
    """
    Select data from a DB table which stores expense tabs' detail to generate a dropdown list.

    Returns:
        list: A dropdown list of expense tab names and IDs as description, and also as ID.
    """
    userid = sysmod.get_current_userid()
    conn = sysmod.db_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(f"SELECT * FROM {Database.SCHEMA_FIN}.expensetab WHERE userid = {userid} AND submitted=FALSE ORDER BY tab_id ASC, tab_name ASC")
        rows = cur.fetchall()
        cur.close()
    content = list((row['tab_name'] + " (" + str(row['tab_id']) + ")", [row['tab_id'], row['tab_name']]) for row in rows)
    return content

@anvil.server.callable("get_selected_expensetab_attr")
@logger.log_function
def get_selected_expensetab_attr(selected_tab):
    """
    Select one particular expense tab attributes from a DB table which stores expense tabs' detail.

    Parameters:
        selected_tab (int): The ID of a selected expense tab.

    Returns:
        list: A row of expense tab attributes including ID and name.
    """
    if selected_tab is None or selected_tab == '':
        return [None, None]
    else:
        conn = sysmod.db_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(f"SELECT * FROM {Database.SCHEMA_FIN}.expensetab WHERE tab_id={selected_tab}")
            row = cur.fetchone()
            cur.close()
        return [row['tab_id'], row['tab_name']]

@anvil.server.callable("select_transactions")
@logger.log_function
def select_transactions(tid):
    """
    Select all transactions under one particular expense tab from a DB table which stores expense tabs' detail.

    Some keys under ExpenseDBTableDefinion require upper cases and convert explicitly as lower cases is default.
    
    Parameters:
        tid (int): The ID of a selected expense tab.

    Returns:
        rows (list): A list of transactions.
    """
    if tid is not None:
        conn = sysmod.db_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(f"SELECT iid, tab_id, trandate AS {exprcd.Date}, account_id AS {exprcd.Account}, \
            amount AS {exprcd.Amount}, labels AS {exprcd.Labels}, remarks AS {exprcd.Remarks}, stmt_dtl AS {exprcd.StmtDtl} \
            FROM {Database.SCHEMA_FIN}.exp_transactions WHERE tab_id = {tid} ORDER BY trandate DESC, iid DESC")
            rows = cur.fetchall()
            logger.trace("rows=", rows)
            # Special handling to make keys found in expense_tbl_def all in upper case to match with client UI, server and DB definition
            # Without this the repeating panel can display none of the data returned from DB as the keys case from dict are somehow auto-lowered
            rows = helper.upper_dict_keys(rows, exprcd.data_list)
            cur.close()
        return list(rows)
    return []

@anvil.server.callable("upsert_transactions")
@logger.log_function
def upsert_transactions(tid, rows):
    """
    Insert of update transactions under one particular expense tab into a DB table.

    Column IID is not generated in application side, it's handled by DB function instead, hence running SQL scripts in DB is required beforehand
    
    Parameters:
        tid (int): The ID of a selected expense tab.
        rows (list): A list of transactions to be inserted or updated.

    Returns:
        iid (list): List of IID following the same sequence as rows when updated successfully, otherwise None. If nothing to update (not error update) then empty list.
    """
    conn = None
    iid = None
    try:
        conn = sysmod.db_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            # Reference for solving the SQL mogrify with multiple groups and update on conflict problems
            # 1. https://www.geeksforgeeks.org/format-sql-in-python-with-psycopgs-mogrify/
            # 2. https://dba.stackexchange.com/questions/161127/column-reference-is-ambiguous-when-upserting-element-into-table
                    
            if len(rows) > 0:
                # debugrecord = [(None, 3201, '2023-03-31', 601, '2', None, '3', '4'), (None, 3201, '2023-03-31', 601, '2', None, '3', '4')]
                mogstr = []
                for row in rows:
                    record = exprcd(row).assign({'tab_id': tid})
                    # decode('utf-8') is essential to allow mogrify function to work properly, reason unknown
                    if record.isvalid(): mogstr.append(cur.mogrify("(%s, %s, %s, %s, %s, %s, %s, %s)", record.to_list()).decode('utf-8'))
                logger.trace("mogstr=", mogstr)
                args = ','.join(mogstr)
                if len(mogstr) > 0:
                    cur.execute("INSERT INTO {schema}.exp_transactions (iid, tab_id, trandate, account_id, amount, labels, \
                    remarks, stmt_dtl) VALUES {p1} ON CONFLICT (iid, tab_id) DO UPDATE SET \
                    trandate=EXCLUDED.trandate, \
                    account_id=EXCLUDED.account_id, \
                    amount=EXCLUDED.amount, \
                    labels=EXCLUDED.labels, \
                    remarks=EXCLUDED.remarks, \
                    stmt_dtl=EXCLUDED.stmt_dtl \
                    WHERE exp_transactions.iid=EXCLUDED.iid AND exp_transactions.tab_id=EXCLUDED.tab_id RETURNING iid".format(schema=Database.SCHEMA_FIN, p1=args))
                    conn.commit()
                    result = cur.fetchall()
                    iid = list(r['iid'] for r in result)
                    logger.debug(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
                    if cur.rowcount != len(rows): raise psycopg2.OperationalError("Transactions (tab id:{0}) creation or update fail.".format(tid))
                else:
                    iid = []
            else:
                iid = []
    except (Exception, psycopg2.OperationalError) as err:
        logger.error(err)
        conn.rollback()
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()        
    return iid
    
@anvil.server.callable("delete_transactions")
@logger.log_function
def delete_transactions(tid, iid_list):
    """
    Delete transactions under one particular expense tab from a DB table.

    One TID contains many transactions, so do many IID. 
    In order to remove some particular transactionsfrom one tab, add these IID into the iid_list.

    Parameters:
        tid (int): The ID of a selected expense tab.
        iid_list (list): A list of IID (item ID) to be deleted, every transaction has an IID.

    Returns:
        count (int): Successful update row count, otherwise None.
    """
    conn, cur, count = [None, None, None]
    try:
        logger.debug("delete iid_list=", iid_list)
        if iid_list is not None and len(iid_list) > 0:
            conn = sysmod.db_connect()
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                args = "({0})".format(",".join(str(i) for i in iid_list))
                cur.execute(f"DELETE FROM {Database.SCHEMA_FIN}.exp_transactions WHERE tab_id = {tid} AND iid IN {args}")
                conn.commit()
                count = cur.rowcount
                logger.debug(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
                if count <= 0: raise psycopg2.OperationalError("Transactions (tab id:{0}) deletion fail.".format(tid))
        else:
            count = 0
    except (Exception, psycopg2.OperationalError) as err:
        logger.error(err)
        conn.rollback()
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()        
    return count

@anvil.server.callable("save_expensetab")
@logger.log_function
def save_expensetab(id, name):
    """
    Save a newly created or existing expense tab detail into a DB table which stores expense tabs' detail.

    This function only saves expense tab's owner ID, name, creation time and last saved time. Does not contain any transactions.
    
    Parameters:
        id (int): The ID of a selected expense tab.
        name (string): The name of a selected expense tab.

    Returns:
        tid['tab_id'] (int): The ID of the newly created or existing expense tab, otherwise None.
    """
    userid = sysmod.get_current_userid()
    try:
        currenttime = datetime.now()
        conn = sysmod.db_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            if id in (None, ''):
                sql = f"INSERT INTO {Database.SCHEMA_FIN}.expensetab (userid, tab_name, submitted, tab_create, tab_lastsave) \
                VALUES ({userid},'{name}',False,'{currenttime}','{currenttime}') RETURNING tab_id"
            else:
                sql = f"UPDATE {Database.SCHEMA_FIN}.expensetab SET tab_name='{name}', submitted=False, tab_create='{currenttime}', tab_lastsave='{currenttime}' \
                WHERE userid={userid} AND tab_id={id} RETURNING tab_id"
            cur.execute(sql)
            conn.commit()
            logger.debug(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
            tid = cur.fetchone()
            if tid['tab_id'] < 0: raise psycopg2.OperationalError("Tab (id:{0}) creation or update fail.".format(template_id))
            return tid['tab_id']
    except (Exception, psycopg2.OperationalError) as err:
        logger.error(err)
        conn.rollback()
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()        
    return None

@anvil.server.callable("submit_expensetab")
@logger.log_function
def submit_expensetab(id, submitted):
    """
    Change an expense tab to either "Submitted" or "Not Submitted" in a DB table which stores expense tabs' detail.

    This function only updates expense tab's submit status and last saved time. Does not contain any transactions.
    
    Parameters:
        id (int): The ID of a selected expense tab.
        submitted (boolean): The to-be-updated submit status of a selected expense tab.

    Returns:
        tid['tab_id'] (int): The ID of the expense tab, otherwise None.
    """
    try:
        currenttime = datetime.now()
        conn = sysmod.db_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            if submitted is True:
                sql = f"UPDATE {Database.SCHEMA_FIN}.expensetab SET submitted={submitted}, tab_submitted='{currenttime}' \
                WHERE tab_id={id} RETURNING tab_id"
            else:
                sql = f"UPDATE {Database.SCHEMA_FIN}.expensetab SET submitted={submitted} WHERE tab_id={id} RETURNING tab_id"
            cur.execute(sql)
            conn.commit()
            logger.debug(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
            tid = cur.fetchone()
            if tid['tab_id'] < 0: raise psycopg2.OperationalError("Tab (id:{0}) submission fail.".format(template_id))
            return tid['tab_id']
    except (Exception, psycopg2.OperationalError) as err:
        logger.error(err)
        conn.rollback()
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()
    return None

@anvil.server.callable("delete_expensetab")
@logger.log_function
def delete_expensetab(tab_id):
    """
    Delete an expense tab from a DB table which stores expense tabs' detail.

    Delete cascade is implemented in expense tabs DB table "tab_id" column, hence transactions under particular tab will be deleted automatically.
    This function only updates expense tab's submit status and last saved time. Does not contain any transactions.
    
    Parameters:
        tab_id (int): The ID of a selected expense tab.

    Returns:
        cur.rowcount (int): Successful update row count, otherwise None.
    """
    try:
        conn = sysmod.db_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(f"DELETE FROM {Database.SCHEMA_FIN}.expensetab WHERE tab_id = {tab_id}")
            conn.commit()
            logger.debug(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
            if cur.rowcount <= 0: raise psycopg2.OperationalError("Expense tab (id:{0}) deletion fail.".format(tab_id))
            return cur.rowcount
    except (Exception, psycopg2.OperationalError) as err:
        logger.error(err)
        conn.rollback()
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()
    return None

@anvil.server.callable("proc_exp_tab_change")
@logger.log_function
def proc_exp_tab_change(tab_id):
    """
    Consolidated process for changing expense tab selection.

    Parameters:
        tab_id (int): The ID of a selected expense tab.

    Returns:
        list: A list of all functions return required by the selection change.
    """
    id, name = get_selected_expensetab_attr(tab_id)
    trx_list = select_transactions(tab_id)
    return [id, name, trx_list]

@anvil.server.callable("proc_save_exp_tab")
@logger.log_function
def proc_save_exp_tab(tab_id, name, rows, iid_list):
    """
    Consolidated process for saving expense tab.

    Parameters:
        tab_id (int): The ID of a selected expense tab.
        name (string): The name of a selected expense tab.
        rows (list): A list of transactions to be inserted or updated.
        iid_list (list): A list of IID (item ID) to be deleted, every transaction has an IID.

    Returns:
        list: A list of all functions return required by the save.
    """
    tab_id = save_expensetab(tab_id, name)
    if tab_id is None or tab_id <= 0:
        raise RuntimeError(f"ERROR: Fail to save expense tab {name}, aborting further update.")
    result_u = upsert_transactions(tab_id, rows)
    result_d = delete_transactions(tab_id, iid_list)
    return [tab_id, result_u, result_d]

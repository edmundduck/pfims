import anvil.server
import psycopg2
import psycopg2.extras
from datetime import date, datetime
from ..DataObject.FinObject import ExpenseRecord as exprcd
from ..Entities.ExpenseTransaction import ExpenseTransaction
from ..Entities.ExpenseTransactionGroup import ExpenseTransactionGroup
from ..ServerUtils import HelperModule as helper
from ..SysProcess import SystemModule as sysmod
from ..SysProcess import LoggingModule
from ..Utils.Constants import Database

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.
logger = LoggingModule.ServerLogger()

@anvil.server.callable("generate_expense_groups_list")
@logger.log_function
def generate_expense_groups_list():
    """
    Select all unsubmitted expense transaction groups from the expense transaction group DB table.

    Returns:
        rows (list of RealDictRow): A list of unsubmitted expense transaction group items.
    """
    userid = sysmod.get_current_userid()
    conn = sysmod.db_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        sql = "SELECT * FROM {schema}.expensetab WHERE userid = {userid} AND submitted=FALSE ORDER BY tab_id ASC, tab_name ASC".format(
            schema=Database.SCHEMA_FIN,
            userid=userid
        )
        cur.execute(sql)
        rows = cur.fetchall()
        cur.close()
        return rows

@anvil.server.callable("select_expense_group")
@logger.log_function
def select_expense_group(exp_grp):
    """
    Return selected expense transaction group detail.

    Parameters:
        exp_grp (ExpenseTransactionGroup): An expense transaction group object.

    Returns:
        exp_grp (ExpenseTransactionGroup): The selected expense transaction group object filled with detail returned from the DB.
    """
    conn = sysmod.db_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        sql = "SELECT {col_def} FROM {schema}.expensetab WHERE tab_id = %s".format(
            col_def=ExpenseTransactionGroup.get_column_definition(),
            schema=Database.SCHEMA_FIN
        )
        stmt = cur.mogrify(sql, (exp_grp.get_id(), ))
        cur.execute(stmt)
        row = cur.fetchone()
        cur.close()
    return ExpenseTransactionGroup(row)

@anvil.server.callable("select_transactions")
@logger.log_function
def select_transactions(exp_grp):
    """
    Return all transactions under a selected expense transaction group.

    Some keys under ExpenseDBTableDefinion require upper cases and convert explicitly as lower cases is default.
    
    Parameters:
        exp_grp (ExpenseTransactionGroup): An expense transaction group object.

    Returns:
        rows (list of ExpenseTransaction): A list of transactions belonging to the group.
    """
    userid = sysmod.get_current_userid()
    conn = sysmod.db_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        sql = "SELECT iid, tab_id, trandate AS {tdate}, account_id AS {account}, amount AS {amount}, \
        labels AS {labels}, remarks AS {remarks}, stmt_dtl AS {stmt_dtl} \
        FROM {schema}.exp_transactions WHERE tab_id = %s ORDER BY trandate DESC, iid DESC".format(
            tdate=exprcd.Date,
            account=exprcd.Account,
            amount=exprcd.Amount,
            labels=exprcd.Labels,
            remarks=exprcd.Remarks,
            stmt_dtl=exprcd.StmtDtl,
            schema=Database.SCHEMA_FIN
        )
        stmt = cur.mogrify(sql, (exp_grp.get_id(), ))
        cur.execute(stmt)
        rows = cur.fetchall()
        logger.trace("rows=", rows)
        # Special handling to make keys found in expense_tbl_def all in upper case to match with client UI, server and DB definition
        # Without this the repeating panel can display none of the data returned from DB as the keys case from dict are somehow auto-lowered
        rows = helper.upper_dict_keys(rows, exprcd.data_list)
        cur.close()
        tnxs = list(ExpenseTransaction(r).set_user_id(userid) for r in rows)
    return tnxs

@anvil.server.callable("upsert_transactions")
@logger.log_function
def upsert_transactions(exp_grp):
    """
    Insert of update transactions under one particular expense transaction group into a DB table.

    Column IID is not generated in application side, it's handled by DB function instead, hence running SQL scripts in DB is required beforehand.
    
    Parameters:
        exp_grp (ExpenseTransactionGroup): An expense transaction group object.

    Returns:
        exp_grp (ExpenseTransactionGroup): An expense transaction group object updated with latest transaction IID.
    """
    def replace_transactions_iid(rp_items, iid):
        """
        Replace all IID from the list of transactions.
    
        Parameters:
            rp_items (list of dict): List of transactions in dict format.
            iid (list of int): New IID list which follows the same order as journals in object.
    
        Returns:
            LD (list of dict): List of transactions with replaced new IID.
        """
        DL = {k: [dic[k] for dic in rp_items] for k in rp_items[0]}
        DL['iid'] = iid
        LD = [dict(zip(DL, col)) for col in zip(*DL.values())]
        return LD

    try:
        cur, conn, iid = [None]*3
        if isinstance(exp_grp, ExpenseTransactionGroup):
            conn = sysmod.db_connect()
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                # Reference for solving the SQL mogrify with multiple groups and update on conflict problems
                # 1. https://www.geeksforgeeks.org/format-sql-in-python-with-psycopgs-mogrify/
                # 2. https://dba.stackexchange.com/questions/161127/column-reference-is-ambiguous-when-upserting-element-into-table                    
                num_rows = len(exp_grp.get_transactions())
                logger.debug(f"num_rows={num_rows}")
                if num_rows > 0:
                    # debugrecord = [(None, 3201, '2023-03-31', 601, '2', None, '3', '4'), (None, 3201, '2023-03-31', 601, '2', None, '3', '4')]
                    mogstr = [cur.mogrify("(%s, %s, %s, %s, %s, %s, %s, %s)", r.get_db_col_list()).decode('utf-8') for r in exp_grp.get_transactions()]
                    logger.trace("mogstr=", mogstr)
                    sql = "INSERT INTO {schema}.exp_transactions (iid, tab_id, trandate, account_id, amount, labels, remarks, stmt_dtl) VALUES {p1} \
                    ON CONFLICT (iid, tab_id) DO UPDATE SET trandate=EXCLUDED.trandate, account_id=EXCLUDED.account_id, amount=EXCLUDED.amount, \
                    labels=EXCLUDED.labels, remarks=EXCLUDED.remarks, stmt_dtl=EXCLUDED.stmt_dtl WHERE exp_transactions.iid=EXCLUDED.iid AND \
                    exp_transactions.tab_id=EXCLUDED.tab_id RETURNING iid".format(schema=Database.SCHEMA_FIN, p1=','.join(mogstr))
                    cur.execute(sql)
                    conn.commit()
                    result = cur.fetchall()
                    iid_list = list(r['iid'] for r in result)
                    logger.debug(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
                    logger.trace(f"iid list={iid_list}")
                    if cur.rowcount != num_rows: raise psycopg2.OperationalError("Transactions under group [{0} ({1})] creation or update fail.".format(exp_grp.get_name(), exp_grp.get_id()))
                    # Transform to list of dict (LD) for simple IID replacement
                    list_tnx_dict = replace_transactions_iid(list(i.get_dict() for i in exp_grp.get_transactions()), iid_list)
                    exp_grp.set_transactions(list_tnx_dict)
                return exp_grp
        raise TypeError('The parameter is not an ExpenseTransactionGroup object.')
    except psycopg2.OperationalError as err:
        logger.error(err)
        conn.rollback()
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()        
    return iid
    
@anvil.server.callable("delete_transactions")
@logger.log_function
def delete_transactions(exp_grp, iid_list):
    """
    Delete transactions under one particular expense transaction group from a DB table.

    One TID contains many transactions, so do many IID. 
    In order to remove some particular transactionsfrom one tab, add these IID into the iid_list.

    Parameters:
        exp_grp (ExpenseTransactionGroup): An expense transaction group object.
        iid_list (list): A list of IID (item ID) to be deleted, every transaction has an IID.

    Returns:
        cur.rowcount (int): Successful update row count, otherwise None.
    """
    try:
        conn, cur = [None] *2
        if isinstance(exp_grp, ExpenseTransactionGroup):
            logger.debug("delete iid_list=", iid_list)
            if iid_list is not None and len(iid_list) > 0:
                conn = sysmod.db_connect()
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                    sql = "DELETE FROM {schema}.exp_transactions WHERE tab_id = %s AND iid IN %s".format(
                        schema=Database.SCHEMA_FIN
                    )
                    stmt = cur.mogrify(sql, (exp_grp.get_id(), tuple(iid_list)))
                    cur.execute(stmt)
                    conn.commit()
                    count = cur.rowcount
                    logger.debug(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
                    if cur.rowcount <= 0: raise psycopg2.OperationalError("Transactions under group [{0} ({1})] deletion fail.".format(exp_grp.get_name(), exp_grp.get_id()))
                    return cur.rowcount
            return 0
        raise TypeError('The parameter is not an ExpenseTransactionGroup object.')
    except psycopg2.OperationalError as err:
        logger.error(err)
        conn.rollback()
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()        
    return None

@anvil.server.callable("create_expense_group")
@logger.log_function
def create_expense_group(exp_grp):
    """
    Create a newly created expense transaction group with detail into an expense transaction group DB table.

    This function only saves expense group's owner ID, name, creation time and last saved time. Does not contain any transactions.
    
    Parameters:
        exp_grp (ExpenseTransactionGroup): An expense transaction group object.

    Returns:
        tid['tab_id'] (int): The ID of the newly created expense transaction group, otherwise None.
    """
    try:
        cur, conn = [None]*2
        if isinstance(exp_grp, ExpenseTransactionGroup):
            userid = sysmod.get_current_userid()
            currenttime = datetime.now()
            conn = sysmod.db_connect()
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                sql = "INSERT INTO {schema}.expensetab (userid, tab_name, submitted, tab_create, tab_lastsave) \
                VALUES (%s,%s,%s,%s,%s) RETURNING tab_id".format(
                    schema=Database.SCHEMA_FIN
                )
                mogstr = [exp_grp.get_user_id(), exp_grp.get_name(), exp_grp.get_submitted_status(), exp_grp.get_created_time(), exp_grp.get_lastsaved_time()]
                stmt = cur.mogrify(sql, mogstr)
                cur.execute(stmt)
                conn.commit()
                logger.debug(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
                tid = cur.fetchone()
                if not tid or tid['tab_id'] < 0: raise psycopg2.OperationalError("Expense transaction group [{0}] creation fail.".format(exp_grp.get_name()))
                return tid['tab_id']
        raise TypeError('The parameter is not an ExpenseTransactionGroup object.')
    except psycopg2.OperationalError as err:
        logger.error(err)
        conn.rollback()
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()        
    return None

@anvil.server.callable("update_expense_group")
@logger.log_function
def update_expense_group(exp_grp):
    """
    Update existing expense transaction group with detail into an expense transaction group DB table.

    This function only saves expense group's owner ID, name, creation time and last saved time. Does not contain any transactions.
    
    Parameters:
        exp_grp (ExpenseTransactionGroup): An expense transaction group object.

    Returns:
        tid['tab_id'] (int): The ID of the existing expense transaction group, otherwise None.
    """
    try:
        cur, conn = [None]*2
        if isinstance(exp_grp, ExpenseTransactionGroup):
            userid = sysmod.get_current_userid()
            currenttime = datetime.now()
            conn = sysmod.db_connect()
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                sql = "UPDATE {schema}.expensetab SET tab_name=%s, submitted=%s, tab_lastsave=%s WHERE userid=%s AND tab_id=%s RETURNING tab_id".format(
                    schema=Database.SCHEMA_FIN
                )
                mogstr = [exp_grp.get_name(), exp_grp.get_submitted_status(), exp_grp.get_lastsaved_time(), exp_grp.get_user_id(), exp_grp.get_id()]
                stmt = cur.mogrify(sql, mogstr)
                cur.execute(stmt)
                conn.commit()
                logger.debug(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
                tid = cur.fetchone()
                if not tid or tid['tab_id'] < 0: raise psycopg2.OperationalError("Expense transaction group [{0} ({1})] update fail.".format(exp_grp.get_name()), exp_grp.get_id())
                return tid['tab_id']
        raise TypeError('The parameter is not an ExpenseTransactionGroup object.')
    except psycopg2.OperationalError as err:
        logger.error(err)
        conn.rollback()
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()        
    return None

@anvil.server.callable("submit_expense_group")
@logger.log_function
def submit_expense_group(exp_grp):
    """
    Submit an expense transaction group to change this group to be either editable (unsubmitted) or not editable (submitted).

    Parameters:
        exp_grp (ExpenseTransactionGroup): An expense transaction group object.

    Returns:
        tid['tab_id'] (int): The ID of the expense tab, otherwise None.
    """
    try:
        cur, conn = [None]*2
        if isinstance(exp_grp, ExpenseTransactionGroup):
            currenttime = datetime.now()
            conn = sysmod.db_connect()
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                submitted = exp_grp.get_submitted_status()
                if submitted:
                    sql = "UPDATE {schema}.expensetab SET submitted=%s, tab_submitted=%s WHERE tab_id=%s RETURNING tab_id".format(
                        schema=Database.SCHEMA_FIN
                    )
                    stmt = cur.mogrify(sql, (submitted, exp_grp.get_submitted_time(), exp_grp.get_id()))
                else:
                    sql = "UPDATE {schema}.expensetab SET submitted=%s WHERE tab_id=%s RETURNING tab_id".format(
                        schema=Database.SCHEMA_FIN
                    )
                    stmt = cur.mogrify(sql, (submitted, exp_grp.get_id()))
                cur.execute(stmt)
                conn.commit()
                logger.debug(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
                tid = cur.fetchone()
                if not tid or tid['tab_id'] < 0: raise psycopg2.OperationalError("Expense transaction group [{0} ({1})] submission fail.".format(exp_grp.get_name()), exp_grp.get_id())
                return tid['tab_id']
        raise TypeError('The parameter is not an ExpenseTransactionGroup object.')
    except psycopg2.OperationalError as err:
        logger.error(err)
        conn.rollback()
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()
    return None

@anvil.server.callable("delete_expense_group")
@logger.log_function
def delete_expense_group(exp_grp):
    """
    Delete an expense transaction group from the expense transaction group DB table.

    Delete cascade is implemented in expense tabs DB table "tab_id" column, hence transactions under particular tab will be deleted automatically.
    This function only updates expense tab's submit status and last saved time. Does not contain any transactions.
    
    Parameters:
        exp_grp (ExpenseTransactionGroup): An expense transaction group object.

    Returns:
        cur.rowcount (int): Successful update row count, otherwise None.
    """
    try:
        cur, conn = [None]*2
        if isinstance(exp_grp, ExpenseTransactionGroup):
            conn = sysmod.db_connect()
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                sql = "DELETE FROM {schema}.expensetab WHERE tab_id = %s".format(
                    schema=Database.SCHEMA_FIN
                )
                stmt = cur.mogrify(sql, (exp_grp.get_id(), ))
                cur.execute(stmt)
                conn.commit()
                logger.debug(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
                if cur.rowcount <= 0: raise psycopg2.OperationalError("Expense transaction group [{0} ({1})] deletion fail.".format(exp_grp.get_name()), exp_grp.get_id())
                return cur.rowcount
        raise TypeError('The parameter is not an ExpenseTransactionGroup object.')
    except psycopg2.OperationalError as err:
        logger.error(err)
        conn.rollback()
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()
    return None

@anvil.server.callable("proc_select_expense_group")
@logger.log_function
def proc_select_expense_group(exp_grp):
    """
    Consolidated process for selecting one expense transaction group.

    Parameters:
        exp_grp (ExpenseTransactionGroup): The selected expense transaction group object.

    Returns:
        exp_grp (ExpenseTransactionGroup): The selected expense transaction group object filled with detail returned from the DB.
    """
    exp_grp = select_expense_group(exp_grp)
    tnx_list = select_transactions(exp_grp)
    exp_grp = exp_grp.set_transactions(tnx_list)
    return exp_grp

@anvil.server.callable("proc_change_expense_group")
@logger.log_function
def proc_change_expense_group(exp_grp, iid_list):
    """
    Consolidated process for making change on expense transaction group and transactions, including creation, update and deletion.

    Parameters:
        exp_grp (ExpenseTransactionGroup): The to-be-changed expense transaction group object.
        iid_list (list): A list of IID (item ID) to be deleted, every transaction has an IID.

    Returns:
        exp_grp (ExpenseTransactionGroup): The expense transaction group object updated with data from DB.
        result_d (int): Successful delete row count, otherwise None.
    """
    tab_id = update_expense_group(exp_grp) if exp_grp.get_id() else create_expense_group(exp_grp)
    if tab_id is None or tab_id <= 0:
        raise RuntimeError(f"ERROR occurs when creating or updating expense transaction group {exp_grp.get_name()}, aborting further update.")
    exp_grp = upsert_transactions(exp_grp)
    result_d = delete_transactions(exp_grp, iid_list)
    return exp_grp, result_d

@anvil.server.callable("init_cache_expense_input")
@logger.log_function
def init_cache_expense_input():
    from . import AccountModule
    from . import LabelModule
    exp_grp_list = generate_expense_groups_list()
    acct_list = AccountModule.generate_accounts_list()
    lbl_list = LabelModule.generate_labels_list()
    return exp_grp_list, acct_list, lbl_list
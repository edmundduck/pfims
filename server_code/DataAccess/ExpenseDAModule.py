import anvil.server
import psycopg2
import psycopg2.extras
from datetime import date, datetime
from .. import SystemProcess as sys
from ..Entities.ExpenseTransaction import ExpenseTransaction
from ..Entities.ExpenseTransactionGroup import ExpenseTransactionGroup
from ..ServerUtils.LoggingModule import ServerLogger
from ..Utils.Constants import Database

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.
logger = ServerLogger()

@anvil.server.callable("generate_expense_groups_list")
@logger.log_function
def generate_expense_groups_list():
    """
    Select all unsubmitted expense transaction groups from the expense transaction group DB table.

    Returns:
        rows (list of RealDictRow): A list of unsubmitted expense transaction group items.
    """
    userid = sys.get_current_userid()
    conn = sys.db_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        sql = "SELECT * FROM {schema}.expensetab WHERE userid = {userid} AND submitted=FALSE ORDER BY tab_id ASC, tab_name ASC".format(
            schema=Database.SCHEMA_FIN,
            userid=userid
        )
        cur.execute(sql)
        rows = cur.fetchall()
        cur.close()
        return rows

@logger.log_function
def select_expense_group(exp_grp):
    """
    Return selected expense transaction group detail.

    Parameters:
        exp_grp (ExpenseTransactionGroup): An expense transaction group object.

    Returns:
        exp_grp (ExpenseTransactionGroup): The selected expense transaction group object filled with detail returned from the DB.
    """
    conn = sys.db_connect()
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

@logger.log_function
def select_transactions(exp_grp):
    """
    Return all transactions under a selected expense transaction group.

    Keys defined in __data_transform_def__ in ExpenseTransaction entity require upper cases and convert explicitly as lower cases is default.
    
    Parameters:
        exp_grp (ExpenseTransactionGroup): An expense transaction group object.

    Returns:
        rows (list of RealDictRow): A list of transactions belonging to the group.
    """
    conn = sys.db_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        sql = "SELECT iid, tab_id, trandate AS {tdate}, account_id AS {account}, amount AS {amount}, \
        labels AS {labels}, remarks AS {remarks}, stmt_dtl AS {stmt_dtl} \
        FROM {schema}.exp_transactions WHERE tab_id = %s ORDER BY trandate DESC, iid DESC".format(
            tdate=ExpenseTransaction.field_date(),
            account=ExpenseTransaction.field_account(),
            amount=ExpenseTransaction.field_amount(),
            labels=ExpenseTransaction.field_labels(),
            remarks=ExpenseTransaction.field_remarks(),
            stmt_dtl=ExpenseTransaction.field_statement_detail(),
            schema=Database.SCHEMA_FIN
        )
        stmt = cur.mogrify(sql, (exp_grp.get_id(), ))
        cur.execute(stmt)
        rows = cur.fetchall()
        logger.trace("rows=", rows)
        cur.close()
        return rows

@logger.log_function
def upsert_transactions(exp_grp):
    """
    Insert of update transactions under one particular expense transaction group into a DB table.

    Column IID is not generated in application side, it's handled by DB function instead, hence running SQL scripts in DB is required beforehand.
    
    Parameters:
        exp_grp (ExpenseTransactionGroup): An expense transaction group object.

    Returns:
        exp_grp (ExpenseTransactionGroup): An expense transaction group object updated with latest transaction IID.
        rows (list of RealDictRow): A list of IID in sequence of the list order in the insert SQL if successful, otherwise None.
    """
    try:
        cur, conn, iid = [None]*3
        if isinstance(exp_grp, ExpenseTransactionGroup):
            conn = sys.db_connect()
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
                    rows = cur.fetchall()
                    logger.debug(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
                    if cur.rowcount != num_rows: raise psycopg2.OperationalError("Transactions under group [{0} ({1})] creation or update fail.".format(exp_grp.get_name(), exp_grp.get_id()))
                    return rows
                return []
        raise TypeError('The parameter is not an ExpenseTransactionGroup object.')
    except psycopg2.OperationalError as err:
        logger.error(err)
        conn.rollback()
        raise psycopg2.OperationalError(err)
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()        
    return None
    
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
                conn = sys.db_connect()
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
            userid = sys.get_current_userid()
            currenttime = datetime.now()
            conn = sys.db_connect()
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
            userid = sys.get_current_userid()
            currenttime = datetime.now()
            conn = sys.db_connect()
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
            conn = sys.db_connect()
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
            conn = sys.db_connect()
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

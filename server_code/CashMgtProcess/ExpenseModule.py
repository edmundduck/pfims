import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import psycopg2
import psycopg2.extras
from datetime import date, datetime
from ..DataObject import FinObject as fobj
from ..System import SystemModule as sysmod
from ..System.LoggingModule import trace, debug, info, warning, error, critical

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.

# Generate expense tabs dropdown items
@anvil.server.callable("generate_expensetabs_dropdown")
@debug.log_function
def generate_expensetabs_dropdown():
    userid = sysmod.get_current_userid()
    conn = sysmod.db_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(f"SELECT * FROM {sysmod.schemafin()}.expensetab WHERE userid = {userid} AND submitted=FALSE ORDER BY tab_id ASC, tab_name ASC")
        rows = cur.fetchall()
        cur.close()
    content = list((row['tab_name'] + " (" + str(row['tab_id']) + ")", [row['tab_id'], row['tab_name']]) for row in rows)
    return content

# Get selected expense tab attributes
@anvil.server.callable("get_selected_expensetab_attr")
@debug.log_function
def get_selected_expensetab_attr(selected_tab):
    if selected_tab is None or selected_tab == '':
        return [None, None]
    else:
        conn = sysmod.db_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(f"SELECT * FROM {sysmod.schemafin()}.expensetab WHERE tab_id={selected_tab}")
            row = cur.fetchone()
            cur.close()
        return [row['tab_id'], row['tab_name']]

# Return transactions for repeating panel to display based on expense tab selection dropdown
@anvil.server.callable("select_transactions")
@debug.log_function
def select_transactions(tid):
    if tid is not None:
        conn = sysmod.db_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(f"SELECT * FROM {sysmod.schemafin()}.exp_transactions WHERE tab_id = {tid} ORDER BY trandate DESC, iid DESC")
            rows = cur.fetchall()
            trace.log("rows=", rows)
            cur.close()
        return list(rows)
    return []

# Insert or update transactions into "exp_transactions" DB table
# Column IID is not generated in application side, it's handled by DB function instead, hence running SQL scripts in DB is required beforehand
@anvil.server.callable("upsert_transactions")
@debug.log_function
def upsert_transactions(tid, rows):
    conn = None
    count = None
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
                    tj = fobj.CashTransaction()
                    tj.assignFromDict({'tab_id': tid}).assignFromDict(row)
                    # decode('utf-8') is essential to allow mogrify function to work properly, reason unknown
                    # mogrify makes the tuple double quoted as string, causing "TypeError: not all arguments converted during string formatting"
                    # also makes None becomes string so cannot be auto converted to NULL when execute
                    # mogstr.append(cur.mogrify("(%s, %s, %s, %s, %s, %s, %s, %s)", tj.getDatabaseRecord()).decode('utf-8'))
                    if tj.isValidRecord(): mogstr.append(tj.getDatabaseRecord())
                trace.log("mogstr=", mogstr)
                if len(mogstr) > 0:
                    cur.executemany("INSERT INTO {schema}.exp_transactions (iid, tab_id, trandate, account_id, amount, labels, \
                    remarks, stmt_dtl) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (iid, tab_id) DO UPDATE SET \
                    trandate=EXCLUDED.trandate, \
                    account_id=EXCLUDED.account_id, \
                    amount=EXCLUDED.amount, \
                    labels=EXCLUDED.labels, \
                    remarks=EXCLUDED.remarks, \
                    stmt_dtl=EXCLUDED.stmt_dtl \
                    WHERE exp_transactions.iid=EXCLUDED.iid AND exp_transactions.tab_id=EXCLUDED.tab_id".format(schema=sysmod.schemafin()), mogstr)
                    conn.commit()
                    count = cur.rowcount
                    debug.log(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
                    if count <= 0: raise psycopg2.OperationalError("Transactions (tab id:{0}) creation or update fail.".format(tid))
                else:
                    count = 0
            else:
                count = 0
    except (Exception, psycopg2.OperationalError) as err:
        error.log(f"{__name__}.{type(err).__name__}: {err}")
        conn.rollback()
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()        
    return count
    
# Delete transactions from "exp_transactions" DB table
@anvil.server.callable("delete_transactions")
@debug.log_function
def delete_transactions(tid, iid_list):
    conn, cur, count = [None, None, None]
    try:
        if iid_list is not None and len(iid_list) > 0:
            conn = sysmod.db_connect()
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                args = "({0})".format(",".join(str(i) for i in iid_list))
                cur.execute(f"DELETE FROM {sysmod.schemafin()}.exp_transactions WHERE tab_id = {tid} AND iid IN {args}")
                conn.commit()
                count = cur.rowcount
                debug.log(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
                if count <= 0: raise psycopg2.OperationalError("Transactions (tab id:{0}) deletion fail.".format(tid))
        else:
            count = 0
    except (Exception, psycopg2.OperationalError) as err:
        error.log(f"{__name__}.{type(err).__name__}: {err}")
        conn.rollback()
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()        
    return count

# Save expense tab
@anvil.server.callable("save_expensetab")
@debug.log_function
def save_expensetab(id, name):
    userid = sysmod.get_current_userid()
    try:
        currenttime = datetime.now()
        conn = sysmod.db_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            if id in (None, ''):
                sql = f"INSERT INTO {sysmod.schemafin()}.expensetab (userid, tab_name, submitted, tab_create, tab_lastsave) \
                VALUES ({userid},'{name}',False,'{currenttime}','{currenttime}') RETURNING tab_id"
            else:
                sql = f"UPDATE {sysmod.schemafin()}.expensetab SET tab_name='{name}', submitted=False, tab_create='{currenttime}', tab_lastsave='{currenttime}' \
                WHERE userid={userid} AND tab_id={id} RETURNING tab_id"
            cur.execute(sql)
            conn.commit()
            debug.log(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
            tid = cur.fetchone()
            if tid['tab_id'] < 0: raise psycopg2.OperationalError("Tab (id:{0}) creation or update fail.".format(template_id))
            return tid['tab_id']
    except (Exception, psycopg2.OperationalError) as err:
        error.log(f"{__name__}.{type(err).__name__}: {err}")
        conn.rollback()
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()        
    return None

# Submit expense tab
@anvil.server.callable("submit_expensetab")
@debug.log_function
def submit_expensetab(id, submitted):
    try:
        currenttime = datetime.now()
        conn = sysmod.db_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            if submitted is True:
                sql = f"UPDATE {sysmod.schemafin()}.expensetab SET submitted={submitted}, tab_submitted='{currenttime}' \
                WHERE tab_id={id} RETURNING tab_id"
            else:
                sql = f"UPDATE {sysmod.schemafin()}.expensetab SET submitted={submitted} WHERE tab_id={id} RETURNING tab_id"
            cur.execute(sql)
            conn.commit()
            debug.log(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
            tid = cur.fetchone()
            if tid['tab_id'] < 0: raise psycopg2.OperationalError("Tab (id:{0}) submission fail.".format(template_id))
            return tid['tab_id']
    except (Exception, psycopg2.OperationalError) as err:
        error.log(f"{__name__}.{type(err).__name__}: {err}")
        conn.rollback()
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()
    return None

# Delete expense tab
# Delete cascade is implemented in "exp_transactions" DB table "tab_id" column, hence transactions under particular tab will be deleted automatically
@anvil.server.callable("delete_expensetab")
@debug.log_function
def delete_expensetab(tab_id):
    try:
        conn = sysmod.db_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(f"DELETE FROM {sysmod.schemafin()}.expensetab WHERE tab_id = {tab_id}")
            conn.commit()
            debug.log(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
            if cur.rowcount <= 0: raise psycopg2.OperationalError("Expense tab (id:{0}) deletion fail.".format(tab_id))
            return cur.rowcount
    except (Exception, psycopg2.OperationalError) as err:
        error.log(f"{__name__}.{type(err).__name__}: {err}")
        conn.rollback()
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()
    return None

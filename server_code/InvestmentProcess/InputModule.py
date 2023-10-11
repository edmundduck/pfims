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
from ..Utils import Constants as const
from ..DataObject import FinObject as fobj
from ..SysProcess import SystemModule as sysmod
from ..SysProcess import LoggingModule

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.
logger = LoggingModule.ServerLogger()

@anvil.server.callable("select_template_journals")
@logger.log_function
def select_template_journals(templ_id):
    """
    Return template journals for repeating panel to display based on template selection dropdown.

    Parameters:
        templ_id (int): Selected template ID from the template's dropdown.

    Returns:
        rows (list): All template journals detail corresponding to the selected template, return empty list otherwise.
    """
    if templ_id is not None:
        conn = sysmod.db_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(f"SELECT * FROM {sysmod.schemafin()}.templ_journals WHERE template_id = {templ_id} ORDER BY sell_date DESC, buy_date DESC, symbol ASC")
            rows = cur.fetchall()
            cur.close()
            return list(rows)
    return []

@anvil.server.callable("upsert_journals")
@logger.log_function
def upsert_journals(tid, rows):
    """
    Insert or update journals into the DB table which stores template journals.

    Column IID is not generated in application side, it's handled by DB function instead, 
    hence running SQL scripts in DB is required beforehand.
    
    Parameters:
        tid (int): The ID of the template. All journals under the same template share the same TID.
        rows (list): The rows of journal data from the repeating panel.

    Returns:
        cur.rowcount (int): Successful update row count, otherwise None.
    """
    try:
        conn = sysmod.db_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            # Reference for solving the SQL mogrify with multiple groups and update on conflict problems
            # 1. https://www.geeksforgeeks.org/format-sql-in-python-with-psycopgs-mogrify/
            # 2. https://dba.stackexchange.com/questions/161127/column-reference-is-ambiguous-when-upserting-element-into-table
            if len(rows) > 0:
                mogstr = []
                for row in rows:
                    tj = fobj.TradeJournal()
                    tj.assignFromDict({'template_id': tid}).assignFromDict(row)
                    # decode('utf-8') is essential to allow mogrify function to work properly, reason unknown
                    mogstr.append(cur.mogrify("(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", tj.getTuple()).decode('utf-8'))
                logger.trace("mogstr=", mogstr)
                args = ",".join(mogstr)
                cur.execute("INSERT INTO {schema}.templ_journals (iid, template_id, sell_date, buy_date, symbol, qty, \
                sales, cost, fee, sell_price, buy_price, pnl) VALUES {p1} ON CONFLICT (iid, template_id) DO UPDATE SET \
                sell_date=EXCLUDED.sell_date, \
                buy_date=EXCLUDED.buy_date, \
                symbol=EXCLUDED.symbol, \
                qty=EXCLUDED.qty, \
                sales=EXCLUDED.sales, \
                cost=EXCLUDED.cost, \
                fee=EXCLUDED.fee, \
                sell_price=EXCLUDED.sell_price, \
                buy_price=EXCLUDED.buy_price, \
                pnl=EXCLUDED.pnl \
                WHERE templ_journals.iid=EXCLUDED.iid AND templ_journals.template_id=EXCLUDED.template_id".format(
                        schema=sysmod.schemafin(),
                        p1=args
                    ))
                conn.commit()
                logger.debug(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
                if cur.rowcount <= 0: raise psycopg2.OperationalError("Journals (template id:{0}) creation or update fail.".format(tid))
                return cur.rowcount
            return 0
    except (Exception, psycopg2.OperationalError) as err:
        logger.error(err)
        conn.rollback()
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()
    return None
    
@anvil.server.callable("delete_journals")
@logger.log_function
def delete_journals(template_id, iid_list):
    """
    Delete journals from the DB table which stores template journals.

    Parameters:
        template_id (int): The ID of the template. All journals under the same template share the same TID.
        iid_list (list): The list of IID requiring deletion.

    Returns:
        cur.rowcount (int): Successful delete row count, otherwise None.
    """
    try:
        if len(iid_list) > 0:
            conn = sysmod.db_connect()
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                args = "({0})".format(",".join(str(i) for i in iid_list))
                cur.execute(f"DELETE FROM {sysmod.schemafin()}.templ_journals WHERE template_id = {template_id} AND iid IN {args}")
                conn.commit()
                logger.debug(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
                if cur.rowcount <= 0: raise psycopg2.OperationalError("Journals (template id:{0}) deletion fail.".format(template_id))
                return cur.rowcount
        return 0
    except (Exception, psycopg2.OperationalError) as err:
        logger.error(err)
        conn.rollback()
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()
    return None

@anvil.server.callable("save_templates")
@logger.log_function
def save_templates(template_id, template_name, broker_id, del_iid = []):
    """
    Insert or update templates into the DB table which stores templates detail with time handling logic.

    Parameters:
        template_id (int): The ID of the template. All journals under the same template share the same TID.
        template_name (string): The name of the template.
        broker_id (string): The broker ID which corresponds to the template.
        del_iid (list): The list of IID requiring deletion.

    Returns:
        tid['template_id'] (int): Template ID if save is successful, otherwise None.
    """
    userid = sysmod.get_current_userid()
    try:
        currenttime = datetime.now()
        conn = sysmod.db_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            if del_iid is not None and len(del_iid) > 0:
                delete_journals(template_id, del_iid)
            if template_id in (None, ''):
                sql = f"INSERT INTO {sysmod.schemafin()}.templates (userid, template_name, broker_id, submitted, template_create, template_lastsave) \
                VALUES ({userid},'{template_name}','{broker_id}',False,'{currenttime}','{currenttime}') RETURNING template_id"
            else:
                sql = f"UPDATE {sysmod.schemafin()}.templates SET template_name = '{template_name}', broker_id = '{broker_id}', \
                submitted = False, template_create = '{currenttime}', template_lastsave = '{currenttime}' \
                WHERE template_id = '{template_id}' RETURNING template_id"
            cur.execute(sql)
            conn.commit()
            logger.debug(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
            tid = cur.fetchone()
            logger.debug("tid=", tid)
            if tid['template_id'] < 0: raise psycopg2.OperationalError("Template (id:{0}) creation or update fail.".format(template_id))
            return tid['template_id']
    except (Exception, psycopg2.OperationalError) as err:
        logger.error(err)
        conn.rollback()
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()
    return None

@anvil.server.callable("submit_templates")
@logger.log_function
def submit_templates(template_id, submitted):
    """
    Update journals into the DB table which stores templates detail to change template submitted/unsubmitted status and timestamp.

    Parameters:
        template_id (int): The ID of the template. All journals under the same template share the same TID.
        submitted (boolean): The to-be-updated submit status of a selected template.

    Returns:
        cur.rowcount (int): Successful submit row count, otherwise None.
    """
    try:
        currenttime = datetime.now()
        conn = sysmod.db_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            if submitted is True:
                sql = f"UPDATE {sysmod.schemafin()}.templates SET submitted = {submitted}, \
                template_submitted = '{currenttime}' WHERE template_id = '{template_id}'"
            else:
                sql = f"UPDATE {sysmod.schemafin()}.templates SET submitted = {submitted} \
                WHERE template_id = '{template_id}'"
            cur.execute(sql)
            conn.commit()
            logger.debug(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
            if cur.rowcount <= 0: raise psycopg2.OperationalError("Templates (id:{0}) submission or reversal fail.".format(template_id))
            return cur.rowcount
    except (Exception, psycopg2.OperationalError) as err:
        logger.error(err)
        conn.rollback()
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()
    return None
  
@anvil.server.callable("delete_templates")
@logger.log_function
def delete_templates(template_id):
    """
    Delete templates from the DB table which stores templates detail.
    
    Delete cascade is implemented in the DB table (which stores template journals detail)"template_id" column, 
    hence journals under particular template will be deleted automatically.

    Parameters:
        template_id (int): The ID of the template. All journals under the same template share the same TID.

    Returns:
        cur.rowcount (int): Successful delete row count, otherwise None.
    """
    try:
        conn = sysmod.db_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(f"DELETE FROM {sysmod.schemafin()}.templates WHERE template_id = {template_id}")
            conn.commit()
            logger.debug(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
            if cur.rowcount <= 0: raise psycopg2.OperationalError("Template (id:{0}) deletion fail.".format(template_id))
            return cur.rowcount
    except (Exception, psycopg2.OperationalError) as err:
        logger.error(err)
        conn.rollback()
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()
    return None

@anvil.server.callable("get_selected_template_attr")
@logger.log_function
def get_selected_template_attr(templ_id):
    """
    Return selected broker based on template dropdown selection.
    
    Parameters:
        templ_id (int): ID of the template.

    Returns:
        row (list): A list of broker ID if select is successful, otherwise None.
    """
    conn = sysmod.db_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(f"SELECT * FROM {sysmod.schemafin()}.templates WHERE template_id={templ_id}")
        row = cur.fetchone()
        logger.trace("row=", row)
        cur.close()
    return row['broker_id'] if row is not None else None
  
@anvil.server.callable("generate_draftring_stock_journal_groups_list")
@logger.log_function
def generate_draftring_stock_journal_groups_list():
    """
    Select DRAFTING (a.k.a. unsubmitted) stock journal groups from the template DB table.

    Returns:
        rows (list of RealDictRow): A list of unsubmitted template item formed by template IDs and names.
    """
    userid = sysmod.get_current_userid()
    conn = sysmod.db_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(f"SELECT * FROM {sysmod.schemafin()}.templates WHERE userid = {userid} AND submitted=false ORDER BY template_id ASC")
        rows = cur.fetchall()
        cur.close()
    return rows

@anvil.server.callable("calculate_amount")
@logger.log_function
def calculate_amount(sell_amt, buy_amt, fee, qty):
    """
    Calculate all amount fields including stock profit and stock unit price during sell or buy.
    
    Parameters:
        sell_amt (float): Lump sum of the stock sold.
        buy_amt (float): Lump sum of the stock purchased.
        fee (float): Fee incurred after stock purchased and sold.
        qty (float): Stock quantity.

    Returns:
        list: A list of stock unit sold price, bought price and profit.
    """
    sell_price = round(float(sell_amt) / float(qty), 2)
    buy_price = round(float(buy_amt) / float(qty), 2)
    profit = round(float(sell_amt) - float(buy_amt) - float(fee), 2)
    return [sell_price, buy_price, profit]

@anvil.server.callable("proc_save_template_and_journals")
@logger.log_function
def proc_save_template_and_journals(template_id, template_name, broker_id, del_iid_list, journals):
    """
    Consolidated process for saving template and journals.

    Parameters:
        template_id (int): The ID of a selected template.
        template_name (string): The name of a selected template.
        broker_id (string): The broker ID which corresponds to the template.
        del_iid_list (list): A list of IID (item ID) to be deleted, every journal has an IID.
        journals (list): A list of journals to be inserted or updated.

    Returns:
        list: A list of all functions return required by the save.
    """
    templ_id = save_templates(template_id, template_name, broker_id, del_iid_list)
    if templ_id is None or templ_id <= 0:
        raise RuntimeError(f"ERROR: Fail to save template {template_name}, aborting further update.")
    result = upsert_journals(templ_id, journals)
    if result is not None:
        select_journals = select_template_journals(templ_id)
    else:
        select_journals = None
    return [templ_id, select_journals]

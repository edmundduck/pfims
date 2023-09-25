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
from ..AdminProcess import ConfigModule as cfmod
from ..DataObject import FinObject as fobj
from ..SysProcess import SystemModule as sysmod
from ..SysProcess import LoggingModule

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.
logger = LoggingModule.ServerLogger()

@anvil.server.callable("get_template_id")
@logger.log_function
def get_template_id(selected_template):
    """
    Retrieve template ID by splitting template dropdown value.

    Parameters:
        selected_template (string): The selected template's name.

    Returns:
        string: A template's ID.
    """
    return selected_template[:selected_template.find("-")].strip() if selected_template is not None and selected_template.find("-") >= 0 else None
  
@anvil.server.callable("generate_template_dropdown_item")
@logger.log_function
def generate_template_dropdown_item(templ_id, templ_name):
    """
    Generate template dropdown text for display in a dropdown list.

    Parameters:
        templ_id (string): The template's ID.
        templ_name (string): The template's name.

    Returns:
        string: A template's dropdown item which comprises the template's ID and name.
    """
    return str(templ_id) + " - " + templ_name

@anvil.server.callable("select_template_journals")
@logger.log_function
def select_template_journals(templ_choice_str):
    """
    Return template journals for repeating panel to display based on template selection dropdown.

    Parameters:
        templ_choice_str (string): Selected value from the template's dropdown.

    Returns:
        rows (list): All template journals detail corresponding to the selected template, return empty list otherwise.
    """
    if templ_choice_str is not None:
        conn = sysmod.db_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(f"SELECT * FROM {sysmod.schemafin()}.templ_journals WHERE template_id = {get_template_id(templ_choice_str)} ORDER BY sell_date DESC, buy_date DESC, symbol ASC")
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
def get_selected_template_attr(templ_choice_str):
    """
    Return selected template name and selected broker based on template dropdown selection.
    
    Parameters:
        templ_choice_str (string): Selected value from the template's dropdown.

    Returns:
        row (list): A list of template name and broker ID if select is successful, otherwise None.
    """
    if templ_choice_str in (None, ''):
        row = cfmod.select_settings()
        return [None, row['default_broker'] if row is not None else '']
    else:
        conn = sysmod.db_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(f"SELECT * FROM {sysmod.schemafin()}.templates WHERE template_id='{get_template_id(templ_choice_str)}'")
            row = cur.fetchone()
            logger.trace("row=", row)
            cur.close()
        return [row['template_name'] if row is not None else None, row['broker_id'] if row is not None else '']
  
@anvil.server.callable("generate_template_dropdown")
@logger.log_function
def generate_template_dropdown():
    """
    Generate DRAFTING (a.k.a. unsubmitted) template selection dropdown items.
    
    Returns:
        row (list): A list of unsubmitted template item formed by template IDs and names.
    """
    userid = sysmod.get_current_userid()
    conn = sysmod.db_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(f"SELECT * FROM {sysmod.schemafin()}.templates WHERE userid = {userid} AND submitted=false ORDER BY template_id ASC")
        rows = cur.fetchall()
        cur.close()
    return list(generate_template_dropdown_item(row['template_id'], row['template_name']) for row in rows)

@anvil.server.callable("cal_profit")
@logger.log_function
def cal_profit(sell, buy, fee):
    """
    Calculate stock profit.
    
    Parameters:
        sell (float): Stock sell price.
        buy (float): Stock buy price.
        fee (float): Fee incurred after stock buy and sell.

    Returns:
        float: Profit of a stock.
    """
    return round(float(sell) - float(buy) - float(fee), 2)

@anvil.server.callable("cal_price")
@logger.log_function
def cal_price(amt, qty):
    """
    Calculate stock unit price during sell or buy
    
    Parameters:
        amt (float): Stock amount.
        qty (float): Stock quantity.

    Returns:
        float: Unit price of a stock.
    """
    return round(float(amt) / float(qty), 2)

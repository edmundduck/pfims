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
from ..System import SystemModule as sysmod

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.

@anvil.server.callable
# Retrieve template ID by splitting template dropdown value
def get_template_id(selected_template):
    return selected_template[:selected_template.find("-")].strip() if selected_template.find("-") >= 0 else None
  
@anvil.server.callable
# Generate template dropdown text for display
def generate_template_dropdown_item(templ_id, templ_name):
    return str(templ_id) + " - " + templ_name

@anvil.server.callable
# Return template journals for repeating panel to display based on template selection dropdown
def select_template_journals(templ_choice_str):
    if templ_choice_str is not None:
        conn = sysmod.db_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(f"SELECT * FROM {sysmod.schemafin()}.templ_journals WHERE template_id = {get_template_id(templ_choice_str)} ORDER BY sell_date DESC, buy_date DESC, symbol ASC")
            rows = cur.fetchall()
            cur.close()
            return list(rows)
    return None

@anvil.server.callable
# Insert or update journals into "templ_journals" DB table
# Column IID is not generated in application side, it's handled by DB function instead, hence running SQL scripts in DB is required beforehand
def upsert_journals(tid, rows):
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
                if cur.rowcount <= 0: raise psycopg2.OperationalError("Journals (template id:{0}) creation or update fail.".format(tid))
                return cur.rowcount
            return 0
    except (Exception, psycopg2.OperationalError) as err:
        sysmod.print_data_debug("OperationalError in " + upsert_journals.__name__, err)
        conn.rollback()
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()
    return None
    
@anvil.server.callable
# Delete journals from "templ_journals" DB table
def delete_journals(template_id, iid_list):
    try:
        if len(iid_list) > 0:
            conn = sysmod.db_connect()
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                args = "({0})".format(",".join(str(i) for i in iid_list))
                cur.execute(f"DELETE FROM {sysmod.schemafin()}.templ_journals WHERE template_id = {template_id} AND iid IN {args}")
                conn.commit()
                if cur.rowcount <= 0: raise psycopg2.OperationalError("Journals (template id:{0}) deletion fail.".format(template_id))
                return cur.rowcount
        return 0
    except (Exception, psycopg2.OperationalError) as err:
        sysmod.print_data_debug("OperationalError in " + delete_journals.__name__, err)
        conn.rollback()
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()
    return None

@anvil.server.callable
# Insert or update templates into "templates" DB table with time handling logic
def save_templates(userid, template_id, template_name, broker_id, del_iid = []):
    try:
        currenttime = datetime.now()
        conn = sysmod.db_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            if len(del_iid) > 0:
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
            tid = cur.fetchone()
            if tid['template_id'] < 0: raise psycopg2.OperationalError("Template (id:{0}) creation or update fail.".format(template_id))
            return tid['template_id']
    except (Exception, psycopg2.OperationalError) as err:
        sysmod.print_data_debug("OperationalError in " + save_templates.__name__, err)
        conn.rollback()
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()
    return None

@anvil.server.callable
# Update journals into "templ_journals" DB table to change template submitted/unsubmitted status and timestamp
def submit_templates(template_id, submitted):
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
            if cur.rowcount <= 0: raise psycopg2.OperationalError("Templates (id:{0}) submission or reversal fail.".format(template_id))
            return cur.rowcount
    except (Exception, psycopg2.OperationalError) as err:
        sysmod.print_data_debug("OperationalError in " + submit_templates.__name__, err)
        conn.rollback()
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()
    return None
  
@anvil.server.callable
# Delete templates from "templates" DB table
# Delete cascade is implemented in "templ_journals" DB table "template_id" column, hence journals under particular template will be deleted automatically
def delete_templates(template_id):
    try:
        conn = sysmod.db_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(f"DELETE FROM {sysmod.schemafin()}.templates WHERE template_id = {template_id}")
            conn.commit()
            if cur.rowcount <= 0: raise psycopg2.OperationalError("Template (id:{0}) deletion fail.".format(template_id))
            return cur.rowcount
    except (Exception, psycopg2.OperationalError) as err:
        sysmod.print_data_debug("OperationalError in " + delete_templates.__name__, err)
        conn.rollback()
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()
    return None

@anvil.server.callable
# Return selected template name and selected broker based on template dropdown selection
def get_selected_template_attr(templ_choice_str, userid):
    if templ_choice_str in (None, ''):
        row = cfmod.select_settings(userid)
        print(f"row={row}")
        return [None, row['default_broker'] if row is not None else '']
    else:
        conn = sysmod.db_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(f"SELECT * FROM {sysmod.schemafin()}.templates WHERE template_id='{get_template_id(templ_choice_str)}'")
            row = cur.fetchone()
            cur.close()
        return [row['template_name'] if row is not None else None, row['broker_id'] if row is not None else '']
  
@anvil.server.callable
# Generate DRAFTING (a.k.a. unsubmitted) template selection dropdown items
def generate_template_dropdown(userid):
    conn = sysmod.db_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(f"SELECT * FROM {sysmod.schemafin()}.templates WHERE userid = {userid} AND submitted=false ORDER BY template_id ASC")
        rows = cur.fetchall()
        cur.close()
    return list(generate_template_dropdown_item(row['template_id'], row['template_name']) for row in rows)

@anvil.server.callable
# Set precision
def cal_profit(sell, buy, fee):
    return round(float(sell) - float(buy) - float(fee), 2)

@anvil.server.callable
# Calculate stock sell/buy price
def cal_price(amt, qty):
    return round(float(amt) / float(qty), 2)

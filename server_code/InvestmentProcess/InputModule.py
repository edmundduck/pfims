import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
#import string
import psycopg2
import psycopg2.extras
from datetime import date, datetime
from .. import global_var
from ..AdminProcess import ConfigModule as cfmod
from ..DataObject import FinObject as fobj
from ..System import SysInternalModule as sysmod

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.
#
# To allow anvil.server.call() to call functions here, we mark
# them with @anvil.server.callable.
# Here is an example - you can replace it with your own:
#
# @anvil.server.callable
# def say_hello(name):
#   print("Hello, " + name + "!")
#   return 42
#

@anvil.server.callable
# Retrieve template ID by splitting template dropdown value
def get_template_id(selected_template):
    if selected_template.find("-") < 0:
        return None
    else:
        return selected_template[:selected_template.find("-")].strip()
  
@anvil.server.callable
# Generate template dropdown text for display
def generate_template_dropdown_item(templ_id, templ_name):
    return str(templ_id) + " - " + templ_name

@anvil.server.callable
# Return journals for repeating panel to display based on sell and buy date criteria
def select_journals(end_date, start_date, symbols):
    conn = sysmod.psqldb_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        sql = "SELECT * FROM {schema}.templ_journals WHERE sell_date='{p1}', buy_date='{p2}'{p3} ORDER BY sell_date DESC, symbols ASC"
        if len(symbols) > 0:
            stmt = sql.format(
                schema=sysmod.schemafin(),
                p1=sell_date,
                p2=buy_date,
                p3=", symbol='" + symbols + "'"
            )
        else:
             stmt = sql.format(
                schema=sysmod.schemafin(),
                p1=sell_date,
                p2=buy_date
            )
        cur.execute(stmt)
        rows = cur.fetchall()
        cur.close()
    return rows

@anvil.server.callable
# Return template journals for repeating panel to display based on template selection dropdown
def select_template_journals(templ_choice_str):
    if not (templ_choice_str is None or templ_choice_str == global_var.input_stock_default_templ_dropdown()):
        conn = sysmod.psqldb_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            sql = "SELECT * FROM {schema}.templ_journals WHERE template_id = {p1} ORDER BY sell_date DESC, buy_date DESC, symbol ASC"
            stmt = sql.format(
                schema=sysmod.schemafin(),
                p1=get_template_id(templ_choice_str)
            )
            cur.execute(stmt)
            rows = cur.fetchall()
            cur.close()
        return list(rows)
    return None

@anvil.server.callable
# Insert or update journals into "templ_journals" DB table
# Column IID is not generated in application side, it's handled by DB function instead, hence running SQL scripts in DB is required beforehand
def upsert_journals(tid, rows):
    try:
        conn = sysmod.psqldb_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            # Reference for solving the SQL mogrify with multiple groups and update on conflict problems
            # 1. https://www.geeksforgeeks.org/format-sql-in-python-with-psycopgs-mogrify/
            # 2. https://dba.stackexchange.com/questions/161127/column-reference-is-ambiguous-when-upserting-element-into-table
            # Following commented section is for INSERT only, not UPSERT
            # args = ",".join(cur.mogrify("(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", tj.assignFromDict(row).getTuple()).decode('utf-8') for row in rows)
            # cur.execute("INSERT INTO {schema}.templ_journals (template_id, sell_date, buy_date, symbol, qty, sales, cost, fee, sell_price, buy_price, pnl) \
            #     VALUES {p1}".format(
            #         schema=sysmod.schemafin(),
            #         p1=args
            #     ))
            # DEBUG TODO remove
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
            count = cur.rowcount
            if count <= 0:
                raise psycopg2.OperationalError("Journals (template id:{0}) creation or update fail.".format(tid))
            cur.close()
        return count
    except psycopg2.OperationalError as err:
        sysmod.print_data_debug("OperationalError in " + upsert_journals.__name__, err)
        conn.rollback()
        cur.close()
        return None
    
@anvil.server.callable
# Delete journals from "templ_journals" DB table
def delete_journals(template_id, iid_list):
    try:
        if len(iid_list) > 0:
            conn = sysmod.psqldb_connect()
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                args = "({0})".format(",".join(str(i) for i in iid_list))
                cur.execute("DELETE FROM " + sysmod.schemafin() + ".templ_journals WHERE template_id = " + template_id + " AND iid IN " + args)
                conn.commit()
                count = cur.rowcount
                if count <= 0:
                    raise psycopg2.OperationalError("Journals (template id:{0}) deletion fail.".format(template_id))
                cur.close()
            return count
        return 0
    except psycopg2.OperationalError as err:
        sysmod.print_data_debug("OperationalError in " + delete_journals.__name__, err)
        conn.rollback()
        cur.close()
        return None

@anvil.server.callable
# Insert or update templates into "templates" DB table with time handling logic
def save_templates(template_id, template_name, broker_id, del_iid = []):
    try:
        currenttime = datetime.now()
        conn = sysmod.psqldb_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            if len(del_iid) > 0:
                delete_journals(template_id, del_iid)
            if template_id is None or template_id == '' or template_id == global_var.input_stock_default_templ_dropdown():
                sql = "INSERT INTO {schema}.templates (template_name, broker_id, submitted, template_create, template_lastsave) \
                VALUES ('{p1}','{p2}',{p3},'{p4}','{p5}') RETURNING template_id"
                stmt = sql.format(
                    schema=sysmod.schemafin(),
                    p1=template_name,
                    p2=broker_id,
                    p3=False,
                    p4=currenttime,
                    p5=currenttime
                )
            else:
                sql = "INSERT INTO {schema}.templates (template_id, template_name, broker_id, submitted, template_create, template_lastsave) \
                VALUES ('{p1}','{p2}','{p3}',{p4},'{p5}','{p6}') ON CONFLICT (template_id) DO UPDATE SET \
                template_name='{p2}', \
                broker_id='{p3}', \
                submitted={p4}, \
                template_create='{p5}', \
                template_lastsave='{p6}' \
                RETURNING template_id"
                stmt = sql.format(
                    schema=sysmod.schemafin(),
                    p1=template_id,
                    p2=template_name,
                    p3=broker_id, 
                    p4=False,
                    p5=currenttime,
                    p6=currenttime,
                )
            cur.execute(stmt)
            conn.commit()
            tid = cur.fetchone()
            if tid['template_id'] < 0:
                    raise psycopg2.OperationalError("Template (id:{0}) creation or update fail.".format(template_id))
            cur.close()
        return tid['template_id']
    except psycopg2.OperationalError as err:
        sysmod.print_data_debug("OperationalError in " + save_templates.__name__, err)
        conn.rollback()
        cur.close()
        return None

@anvil.server.callable
# Update journals into "templ_journals" DB table to change template submitted/unsubmitted status and timestamp
def submit_templates(template_id, submitted):
    try:
        currenttime = datetime.now()
        conn = sysmod.psqldb_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            if submitted is True:
                sql = "INSERT INTO {schema}.templates (template_id, submitted, template_submitted) \
                VALUES ('{p1}',{p2},'{p3}') ON CONFLICT (template_id) DO UPDATE SET \
                submitted={p2}, template_submitted='{p3}' \
                "
                stmt = sql.format(
                    schema=sysmod.schemafin(),
                    p1=template_id,
                    p2=submitted,
                    p3=currenttime
                )
            else:
                sql = "INSERT INTO {schema}.templates (template_id, submitted) \
                VALUES ('{p1}',{p2}) ON CONFLICT (template_id) DO UPDATE SET \
                submitted={p2} \
                "
                stmt = sql.format(
                    schema=sysmod.schemafin(),
                    p1=template_id,
                    p2=submitted
                )
            cur.execute(stmt)
            conn.commit()
            count = cur.rowcount
            if count <= 0:
                raise psycopg2.OperationalError("Templates (id:{0}) submission or reversal fail.".format(template_id))
            cur.close()
        return count
    except psycopg2.OperationalError as err:
        sysmod.print_data_debug("OperationalError in " + submit_templates.__name__, err)
        conn.rollback()
        cur.close()
        return None
  
@anvil.server.callable
# Delete templates from "templates" DB table
# Delete cascade is implemented in "templ_journals" DB table "template_id" column, hence journals under particular template will be deleted automatically
def delete_templates(template_id):
    try:
        conn = sysmod.psqldb_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("DELETE FROM " + sysmod.schemafin() + ".templates WHERE template_id = " + template_id)
            conn.commit()
            count = cur.rowcount
            if count <= 0:
                raise psycopg2.OperationalError("Template (id:{0}) deletion fail.".format(template_id))
            cur.close()
        return count
    except psycopg2.OperationalError as err:
        sysmod.print_data_debug("OperationalError in " + delete_templates.__name__, err)
        conn.rollback()
        # TODO - cur can be referenced before assignment if psqldb_connect fails before cur declared
        cur.close()
        return None

@anvil.server.callable
# Return selected template name and selected broker based on template dropdown selection
def get_selected_template_attr(templ_choice_str):
    if templ_choice_str is None or templ_choice_str == '' or templ_choice_str == global_var.input_stock_default_templ_dropdown():
        row = cfmod.select_settings()
        return [global_var.input_stock_default_templ_name(), row['default_broker'] if row is not None else '']
    else:
        conn = sysmod.psqldb_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            sql = "SELECT * FROM {schema}.templates WHERE template_id='{p1}'"   
            stmt = sql.format(
                schema=sysmod.schemafin(),
                p1=get_template_id(templ_choice_str)
            )
            cur.execute(stmt)
            row = cur.fetchone()
            cur.close()
        return [row['template_name'] if row is not None else global_var.input_stock_default_templ_name(), row['broker_id'] if row is not None else '']
  
@anvil.server.callable
# Generate DRAFTING (a.k.a. unsubmitted) template selection dropdown items
def generate_template_dropdown():
    conn = sysmod.psqldb_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        sql = "SELECT * FROM {schema}.templates WHERE submitted=false ORDER BY template_id ASC"
        stmt = sql.format(
            schema=sysmod.schemafin()
        )
        cur.execute(stmt)
        rows = cur.fetchall()
        cur.close()
    content = list(generate_template_dropdown_item(row['template_id'], row['template_name']) for row in rows)
    content.insert(0, global_var.input_stock_default_templ_dropdown())
    return content

@anvil.server.callable
# Return template journals for csv generation
def generate_csv(end_date, start_date, symbols):
    return select_journals(end_date, start_date, symbols).to_csv()

@anvil.server.callable
# Set precision
def cal_profit(sell, buy, fee):
    return round(float(sell) - float(buy) - float(fee), 2)

@anvil.server.callable
# Calculate stock sell/buy price
def cal_price(amt, qty):
    return round(float(amt) / float(qty), 2)

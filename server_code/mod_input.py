import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import random
import string
from datetime import date, datetime
from . import mod_debug
from . import mod_setting
from . import global_var
from . import FinObject as fobj
# Postgres impl START
import psycopg2
import psycopg2.extras
# Postgres impl END

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

# Static variables
DEFAULT_NEW_TEMPL_TEXT = "[NEW]"
DEFAULT_NEW_TEMPL_NAME = "NewTemplate"

# Internal function - Retrieve template ID by splitting template dropdown value
def split_templ_id(templ_id):
    if templ_id.find("-") < 0:
        return None
    else:
        return templ_id[:templ_id.find("-")].strip()

# Establish Postgres DB connection (Yugabyte DB)
def psqldb_connect():
    connection = psycopg2.connect(
        dbname='pfimsdb',
        host='europe-west2.793f25ab-3df2-4832-b84a-af6bdc81f2c7.gcp.ybdb.io',
        port='5433',
        user=anvil.secrets.get_secret('yugadb_app_usr'),
        password=anvil.secrets.get_secret('yugadb_app_pw'))
    return connection

@anvil.server.callable
# DB table "templ_journals" select method from external DB callable by client modules
def select_templ_journals(end_date, start_date, symbols):
    conn = psqldb_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        sql = "SELECT * FROM {schema}.templ_journals WHERE \
            sell_date='{p1}', \
            buy_date='{p2}'{p3} \
            ORDER BY sell_date DESC, symbols ASC"
        if len(symbols) > 0:
            stmt = sql.format(
                schema=global_var.schemafin(),
                p1=sell_date,
                p2=buy_date,
                p3=", symbol='" + symbols + "'"
            )
        else:
             stmt = sql.format(
                schema=global_var.schemafin(),
                p1=sell_date,
                p2=buy_date
            )
        cur.execute(stmt)
        rows = cur.fetchall()
        cur.close()
    return rows

@anvil.server.callable
# DB table "templ_journals" update/insert method to external DB callable by client modules
# def upsert_templ_journals(journal):
def upsert_templ_journals(tid, rows):
    try:
        conn = psqldb_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            tj = fobj.TradeJournal()
            tj.assignFromDict({'template_id': tid})
            for row in rows:
                tj.assignFromDict(row)
                mod_debug.print_data_debug("a", str(cur.mogrify("(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", tj.getTuple())))
                args = ",".join(str(cur.mogrify("(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", tj.getTuple())))
            cur.execute("INSERT INTO {schema}.templ_journals (template_id, sell_date, buy_date, symbol, qty, sales, cost, fee, sell_price, buy_price, pnl) \
                VALUES {p1}".format(
                    schema=global_var.schemafin(),
                    p1=args
                ))
            # sql = "INSERT INTO {schema}.templ_journals (template_id, sell_date, buy_date, symbol, qty, sales, cost, fee, sell_price, buy_price, pnl) \
            # VALUES ('{p1}','{p2}','{p3}','{p4}','{p5}','{p6}','{p7})','{p8}','{p9}','{p10}','{p11}' \
            # ON CONFLICT (iid) DO UPDATE SET \
            # template_id='{p1}', \
            # sell_date='{p2}', \
            # buy_date='{p3}', \
            # symbol='{p4}', \
            # qty='{p5}', \
            # sales='{p6}', \
            # cost='{p7}', \
            # fee='{p8}', \
            # sell_price='{p9}', \
            # buy_price='{p10}', \
            # pnl='{p11}' \
            # "    
            # stmt = sql.format(
            #     schema=global_var.schemafin(),
            #     p1=journal.template_id,
            #     p2=journal.sell_date,
            #     p3=journal.buy_date,
            #     p4=journal.symbol,
            #     p5=journal.qty,
            #     p6=journal.sales,
            #     p7=journal.cost,
            #     p8=journal.fee,
            #     p9=journal.sell_price,
            #     p10=journal.buy_price,
            #     p11=journal.pnl
            # )
            conn.commit()
            count = cur.rowcount
            if count <= 0:
                raise psycopg2.OperationalError("Delete fail.")
            cur.close()
        return count
    except psycopg2.OperationalError as err:
        mod_debug.print_data_debug("OperationalError in " + delete_templ_journals.__name__, err)
        conn.rollback()
        cur.close()
        return None
    
@anvil.server.callable
# DB table "templ_journals" delete method to external DB callable by client modules
def delete_templ_journals(template_id, iid):
    try:
        conn = psqldb_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("DELETE FROM " + global_var.schemafin() + ".templ_journals WHERE template_id = " + template_id + " AND iid = " + iid)
            conn.commit()
            count = cur.rowcount
            if count <= 0:
                raise psycopg2.OperationalError("Delete fail.")
            cur.close()
        return count
    except psycopg2.OperationalError as err:
        mod_debug.print_data_debug("OperationalError in " + delete_templ_journals.__name__, err)
        conn.rollback()
        cur.close()
        return None

@anvil.server.callable
# Generate template dropdown text for display
def merge_templ_id_name(templ_id, templ_name):
    return str(templ_id) + " - " + templ_name

@anvil.server.callable
# DB table "templates" update/insert method with time handling logic
def upsert_templates(template_id, template_name, broker_id):
    try:
        currenttime = datetime.now()
        conn = psqldb_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            if template_id is None or template_id == '' or template_id == DEFAULT_NEW_TEMPL_TEXT:
                sql = "INSERT INTO {schema}.templates (template_name, template_create, template_lastsave) \
                VALUES ('{p1}','{p2}','{p3}') RETURNING template_id"
                stmt = sql.format(
                    schema=global_var.schemafin(),
                    p1=template_name,
                    p2=currenttime,
                    p3=currenttime
                )
            else:
                sql = "INSERT INTO {schema}.templates (template_id, template_name, submitted, template_create, template_lastsave) \
                VALUES ('{p1}','{p2}','{p3}','{p4}','{p5}' \
                ON CONFLICT (template_id) DO UPDATE SET \
                template_name='{p2}', \
                submitted='{p3}', \
                template_create='{p4}', \
                template_lastsave='{p5}' \
                RETURNING template_id"
                stmt = sql.format(
                    schema=global_var.schemafin(),
                    p1=template_id,
                    p2=template_name,
                    p3=false,
                    p4=currenttime,
                    p5=currenttime,
                )
            cur.execute(stmt)
            conn.commit()
            tid = cur.fetchone()
            if tid['template_id'] < 0:
                    raise psycopg2.OperationalError("Insert/Update fail.")                
            cur.close()
        return tid['template_id']
    except psycopg2.OperationalError as err:
        mod_debug.print_data_debug("OperationalError in " + upsert_templates.__name__, err)
        conn.rollback()
        cur.close()
        return None

@anvil.server.callable
# DB table "templates" update/insert method for submit/unsubmit
def update_templates_submit_flag(template_id, submitted):
    currenttime = datetime.now()
    try:
        conn = psqldb_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            if submitted is True:
                sql = "INSERT INTO {schema}.templates (template_id, submitted, template_submitted) \
                VALUES ('{p1}','{p2}','{p3}') \
                ON CONFLICT (template_id) DO UPDATE SET \
                submitted='{p2}', template_submitted='{p3}' \
                "
                stmt = sql.format(
                    schema=global_var.schemafin(),
                    p1=template_id,
                    p2=submitted,
                    p3=currenttime
                )
            else:
                sql = "INSERT INTO {schema}.templates (template_id, submitted) \
                VALUES ('{p1}','{p2}') \
                ON CONFLICT (template_id) DO UPDATE SET \
                submitted='{p2}' \
                "
                stmt = sql.format(
                    schema=global_var.schemafin(),
                    p1=template_id,
                    p2=submitted
                )
            conn.commit()
            count = cur.rowcount
            if count <= 0:
                raise psycopg2.OperationalError("Delete fail.")
            cur.close()
        return count
    except psycopg2.OperationalError as err:
        mod_debug.print_data_debug("OperationalError in " + update_templates_submit_flag.__name__, err)
        conn.rollback()
        cur.close()
        return None
  
@anvil.server.callable
# DB table "templates" delete method
def delete_templates(template_id):
    rows = app_tables.templates.search(template_id=template_id)
    if len(list(rows)) != 0:
        for r in rows:
            r.delete()

@anvil.server.callable
# Random generate new template ID with 4 alphabets + 1 digit = 26^4 * 9 combinations if it is a new template
# Otherwise return the selected template ID
def get_templ_id(templ_choice_str):
    return split_templ_id(templ_choice_str)
  
@anvil.server.callable
# Update template name based on template dropdown selection
def get_input_templ_name(templ_choice_str):
    if templ_choice_str is None or templ_choice_str == '' or templ_choice_str == DEFAULT_NEW_TEMPL_TEXT:
        return DEFAULT_NEW_TEMPL_NAME
    else:
        conn = psqldb_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            template_id=split_templ_id(templ_choice_str)
            sql = "SELECT * FROM {schema}.templates WHERE \
                template_id='{p1}'"   
            stmt = sql.format(
                schema=global_var.schemafin(),
                p1=template_id)
            cur.execute(stmt)
            row = cur.fetchone()
            cur.close()
        return row['template_name'] if row is not None else DEFAULT_NEW_TEMPL_NAME
  
@anvil.server.callable
# Return broker name based on template dropdown selection
def get_input_templ_broker(templ_choice_str):
    if templ_choice_str is None or templ_choice_str == '' or templ_choice_str == DEFAULT_NEW_TEMPL_TEXT:
        row = mod_setting.select_settings()
        return row['default_broker'] if row is not None else ''
    else:
        template_id=split_templ_id(templ_choice_str)
        conn = psqldb_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            template_id=split_templ_id(templ_choice_str)
            sql = "SELECT * FROM {schema}.templates WHERE \
                template_id='{p1}'"   
            stmt = sql.format(
                schema=global_var.schemafin(),
                p1=template_id)
            cur.execute(stmt)
            row = cur.fetchone()
            cur.close()
        return row['broker_id'] if row is not None else ''
    
@anvil.server.callable
# Generate DRAFTING template selection dropdown items
def get_input_templ_list():
    conn = psqldb_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        sql = "SELECT * FROM {schema}.templates WHERE submitted=false ORDER BY template_id ASC"
        stmt = sql.format(
            schema=global_var.schemafin()
        )
        cur.execute(stmt)
        rows = cur.fetchall()
        cur.close()
    content = list(merge_templ_id_name(row['template_id'], row['template_name']) for row in rows)
    content.insert(0, DEFAULT_NEW_TEMPL_TEXT)
    return content

@anvil.server.callable
# Return template items for repeating panel to display based on template selection dropdown
def get_input_templ_items(templ_choice_str):
    listitems = []
    if not (templ_choice_str is None or templ_choice_str == DEFAULT_NEW_TEMPL_TEXT):
        template_id=split_templ_id(templ_choice_str)
        conn = psqldb_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            sql = "SELECT * FROM {schema}.templ_journals WHERE template_id = {p1} \
                ORDER BY sell_date DESC, buy_date DESC, symbol ASC"
            stmt = sql.format(
                schema=global_var.schemafin(),
                p1=template_id
            )
            cur.execute(stmt)
            rows = cur.fetchall()
            cur.close()
        listitems = list(rows)
    return listitems

@anvil.server.callable
# Return template items for csv generation
def generate_csv(end_date, start_date, symbols):
    return select_templ_journals(end_date, start_date, symbols).to_csv()

@anvil.server.callable
# Set precision
def cal_profit(sell, buy, fee):
    return round(float(sell) - float(buy) - float(fee), 2)

@anvil.server.callable
# Calculate stock sell/buy price
def cal_price(amt, qty):
    return round(float(amt) / float(qty), 2)

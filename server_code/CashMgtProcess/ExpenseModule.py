import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import psycopg2
import psycopg2.extras
from datetime import date, datetime
from ..System import SystemModule as sysmod

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
# Generate currency dropdown items
def generate_ccy_dropdown():
    conn = sysmod.psqldb_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        sql = "SELECT * FROM {schema}.ccy ORDER BY common_seq ASC, abbv ASC"
        stmt = sql.format(
            schema=sysmod.schemafin()
        )
        cur.execute(stmt)
        rows = cur.fetchall()
        cur.close()
    content = list((row['abbv'] + " " + row['name'] + " (" + row['symbol'] + ")" if row['symbol'] else row['abbv'] + " " + row['name'], row['abbv']) for row in rows)
    return content

@anvil.server.callable
# Generate accounts dropdown items
def generate_accounts_dropdown():
    conn = sysmod.psqldb_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        sql = "SELECT * FROM {schema}.accounts ORDER BY status ASC, valid_to DESC, valid_from DESC"
        stmt = sql.format(
            schema=sysmod.schemafin()
        )
        cur.execute(stmt)
        rows = cur.fetchall()
        cur.close()
    content = list((row['name'] + " (" + str(row['id']) + ")", [row['id'], row['name']]) for row in rows)
    return content

@anvil.server.callable
# Generate expense tabs dropdown items
def generate_expensetabs_dropdown():
    conn = sysmod.psqldb_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        sql = "SELECT * FROM {schema}.expensetab ORDER BY tab_id ASC, tab_name ASC"
        stmt = sql.format(
            schema=sysmod.schemafin()
        )
        cur.execute(stmt)
        rows = cur.fetchall()
        cur.close()
    content = list((row['tab_name'] + " (" + str(row['tab_id']) + ")", [row['tab_id'], row['tab_name']]) for row in rows)
    return content

@anvil.server.callable
# Get selected account attributes
def get_selected_account_attr(selected_acct):
    if selected_acct is None or selected_acct == '':
        return [None, None, None, None, None, True]
    else:
        conn = sysmod.psqldb_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            sql = "SELECT * FROM {schema}.accounts WHERE id={p1}"   
            stmt = sql.format(
                schema=sysmod.schemafin(),
                p1=selected_acct
            )
            cur.execute(stmt)
            row = cur.fetchone()
            cur.close()
        return [row['id'], row['name'], row['ccy'], row['valid_from'], row['valid_to'], row['status']]

@anvil.server.callable
# Get selected expense tab attributes
def get_selected_expensetab_attr(selected_tab):
    if selected_tab is None or selected_tab == '':
        return [None, None]
    else:
        conn = sysmod.psqldb_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            sql = "SELECT * FROM {schema}.expensetab WHERE tab_id={p1}"   
            stmt = sql.format(
                schema=sysmod.schemafin(),
                p1=selected_tab
            )
            cur.execute(stmt)
            row = cur.fetchone()
            cur.close()
        return [row['tab_id'], row['tab_name']]

@anvil.server.callable
# Create account
def create_account(name, ccy, valid_from, valid_to, status):
    try:
        conn = sysmod.psqldb_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            sql = "INSERT INTO {schema}.accounts (name, ccy, valid_from, valid_to, status) \
            VALUES ('{p1}','{p2}','{p3}','{p4}',{p5}) RETURNING id"
            stmt = sql.format(
                schema=sysmod.schemafin(),
                p1=name,
                p2=ccy,
                p3=valid_from,
                p4=valid_to,
                p5=status
            )
            cur.execute(stmt)
            conn.commit()
            id = cur.fetchone()
            if id['id'] < 0:
                    raise psycopg2.OperationalError("Account ({0}) creation fail.".format(name))
            cur.close()
        return id['id']
    except psycopg2.OperationalError as err:
        sysmod.print_data_debug("OperationalError in " + create_accounts.__name__, err)
        conn.rollback()
        cur.close()
        return None

@anvil.server.callable
# Update account
def update_account(id, name, ccy, valid_from, valid_to, status):
    try:
        conn = sysmod.psqldb_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            sql = "UPDATE {schema}.accounts SET name='{p2}', ccy='{p3}', valid_from='{p4}', valid_to='{p5}', status={p6} \
            WHERE id={p1}"
            stmt = sql.format(
                schema=sysmod.schemafin(),
                p1=id,
                p2=name,
                p3=ccy,
                p4=valid_from,
                p5=valid_to,
                p6=status
            )
            cur.execute(stmt)
            conn.commit()
            count = cur.rowcount
            if count <= 0:
                    raise psycopg2.OperationalError("Account ({0}) update fail.".format(name))
            cur.close()
        return count
    except psycopg2.OperationalError as err:
        sysmod.print_data_debug("OperationalError in " + update_account.__name__, err)
        conn.rollback()
        cur.close()
        return None

@anvil.server.callable
# Delete account
def delete_account(id):
    try:
        conn = sysmod.psqldb_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            sql = "DELETE FROM {schema}.accounts WHERE id={p1}"
            stmt = sql.format(
                schema=sysmod.schemafin(),
                p1=id,
            )
            cur.execute(stmt)
            conn.commit()
            count = cur.rowcount
            if count <= 0:
                    raise psycopg2.OperationalError("Account ({0}) deletion fail.".format(name))
            cur.close()
        return count
    except psycopg2.OperationalError as err:
        sysmod.print_data_debug("OperationalError in " + delete_account.__name__, err)
        conn.rollback()
        cur.close()
        return None

@anvil.server.callable
# Save expense tab
def save_expensetab(id, name):
    try:
        currenttime = datetime.now()
        conn = sysmod.psqldb_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            if id is None or id == '':
                sql = "INSERT INTO {schema}.expensetab (tab_name, submitted, tab_create, tab_lastsave) \
                VALUES ('{p1}',{p2},'{p3}','{p4}') RETURNING tab_id"
                stmt = sql.format(
                    schema=sysmod.schemafin(),
                    p1=name,
                    p2=False,
                    p3=currenttime,
                    p4=currenttime
                )
            else:
                sql = "INSERT INTO {schema}.expensetab (tab_id, tab_name, submitted, tab_create, tab_lastsave) \
                VALUES ('{p1}','{p2}','{p3}',{p4},'{p5}','{p6}') ON CONFLICT (tab_id) DO UPDATE SET \
                tab_name='{p2}', \
                submitted={p3}, \
                tab_create='{p4}', \
                tab_lastsave='{p5}' \
                RETURNING tab_id"
                stmt = sql.format(
                    schema=sysmod.schemafin(),
                    p1=id,
                    p2=name,
                    p3=False,
                    p4=currenttime,
                    p5=currenttime,
                )
            cur.execute(stmt)
            conn.commit()
            tid = cur.fetchone()
            if tid['tab_id'] < 0:
                    raise psycopg2.OperationalError("Tab (id:{0}) creation or update fail.".format(template_id))
            cur.close()
        return tid['tab_id']
    except psycopg2.OperationalError as err:
        sysmod.print_data_debug("OperationalError in " + save_expensetab.__name__, err)
        conn.rollback()
        cur.close()
        return None

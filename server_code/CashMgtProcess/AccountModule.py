import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import psycopg2
import psycopg2.extras
from ..System import SystemModule as sysmod

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.

@anvil.server.callable
# Generate accounts dropdown items for account maintenance form
def generate_accounts_dropdown(userid):
    conn = sysmod.db_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(f"SELECT * FROM {sysmod.schemafin()}.accounts WHERE userid = {userid} ORDER BY status ASC, valid_from DESC, valid_to DESC, id DESC")
        rows = cur.fetchall()
        cur.close()
    return list((row['name'] + " (" + str(row['id']) + ")", [row['id'], row['name']]) for row in rows)

@anvil.server.callable
# Generate currency dropdown items
def generate_ccy_dropdown():
    conn = sysmod.db_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(f"SELECT * FROM {sysmod.schemarefd()}.ccy ORDER BY common_seq ASC, abbv ASC")
        rows = cur.fetchall()
        cur.close()
    content = list((row['abbv'] + " " + row['name'] + " (" + row['symbol'] + ")" if row['symbol'] else row['abbv'] + " " + row['name'], row['abbv']) for row in rows)
    return content

@anvil.server.callable
# Get selected account attributes
def get_selected_account_attr(selected_acct):
    if selected_acct in (None, ''):
        return [None, None, None, None, None, True]
    else:
        conn = sysmod.db_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            sql = "SELECT * FROM {schema}.accounts WHERE id=%s".format(schema=sysmod.schemafin())  
            stmt = cur.mogrify(sql, (selected_acct, ))
            cur.execute(stmt)
            row = cur.fetchone()
            cur.close()
        return [row['id'], row['name'], row['ccy'], row['valid_from'], row['valid_to'], row['status']]

@anvil.server.callable
# Create account
def create_account(userid, name, ccy, valid_from, valid_to, status):
    try:
        conn = sysmod.db_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            sql = "INSERT INTO {schema}.accounts (userid, name, ccy, valid_from, valid_to, status) \
            VALUES (%s,%s,%s,%s,%s,%s) RETURNING id".format(schema=sysmod.schemafin())
            stmt = cur.mogrify(sql, (userid, name, ccy, valid_from, valid_to, status))
            cur.execute(stmt)
            conn.commit()
            id = cur.fetchone()
            if id['id'] < 0: raise psycopg2.OperationalError("Account ({0}) creation fail.".format(name))
            return id['id']
    except (Exception, psycopg2.OperationalError) as err:
        sysmod.print_data_debug("OperationalError in " + create_accounts.__name__, err)
        conn.rollback()
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()
    return None

@anvil.server.callable
# Update account
def update_account(id, name, ccy, valid_from, valid_to, status):
    try:
        conn = sysmod.db_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            sql = "UPDATE {schema}.accounts SET name=%s, ccy=%s, valid_from=%s, valid_to=%s, status=%s WHERE id=%s".format(schema=sysmod.schemafin())
            stmt = cur.mogrify(sql, (name, ccy, valid_from, valid_to, status, id))
            cur.execute(stmt)
            conn.commit()
            if cur.rowcount <= 0: raise psycopg2.OperationalError("Account ({0}) update fail.".format(name))
            return cur.rowcount
    except (Exception, psycopg2.OperationalError) as err:
        sysmod.print_data_debug("OperationalError in " + update_account.__name__, err)
        conn.rollback()
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()
    return None

@anvil.server.callable
# Delete account
def delete_account(id):
    try:
        conn = sysmod.db_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            sql = "DELETE FROM {schema}.accounts WHERE id=%s".format(schema=sysmod.schemafin())
            stmt = cur.mogrify(sql, (id, ))
            cur.execute(stmt)
            conn.commit()
            if cur.rowcount <= 0: raise psycopg2.OperationalError("Account ({0}) deletion fail.".format(name))
            return cur.rowcount
    except (Exception, psycopg2.OperationalError) as err:
        sysmod.print_data_debug("OperationalError in " + delete_account.__name__, err)
        conn.rollback()
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()
    return None

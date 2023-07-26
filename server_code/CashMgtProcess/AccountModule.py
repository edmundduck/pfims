import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import psycopg2
import psycopg2.extras
from ..System import SystemModule as sysmod
from ..System.LoggingModule import logger

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.

# Generate accounts dropdown items for account maintenance form
# For callable decorator to be used with other decorator, refer to following,
# https://anvil.works/forum/t/fixed-multiple-decorators-in-forms/3582/5
@anvil.server.callable("generate_accounts_dropdown")
@logger.log_function
def generate_accounts_dropdown():
    userid = sysmod.get_current_userid()
    conn = sysmod.db_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(f"SELECT * FROM {sysmod.schemafin()}.accounts WHERE userid = {userid} ORDER BY status ASC, valid_from DESC, valid_to DESC, id DESC")
        rows = cur.fetchall()
        logger.trace("rows=", rows)
        cur.close()
    return list((row['name'] + " (" + str(row['id']) + ")", [row['id'], row['name']]) for row in rows)

# Generate currency dropdown items
@anvil.server.callable("generate_ccy_dropdown")
@logger.log_function
def generate_ccy_dropdown():
    conn = sysmod.db_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(f"SELECT * FROM {sysmod.schemarefd()}.ccy ORDER BY common_seq ASC, abbv ASC")
        rows = cur.fetchall()
        logger.trace("rows=", rows)
        cur.close()
    content = list((row['abbv'] + " " + row['name'] + " (" + row['symbol'] + ")" if row['symbol'] else row['abbv'] + " " + row['name'], row['abbv']) for row in rows)
    return content

# Get selected account attributes
@anvil.server.callable("get_selected_account_attr")
@logger.log_function
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
            logger.trace("row=", row)
            cur.close()
        return [row['id'], row['name'], row['ccy'], row['valid_from'], row['valid_to'], row['status']]

# Create account
@anvil.server.callable("create_account")
@logger.log_function
def create_account(name, ccy, valid_from, valid_to, status):
    try:
        userid = sysmod.get_current_userid()
        conn = sysmod.db_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            sql = "INSERT INTO {schema}.accounts (userid, name, ccy, valid_from, valid_to, status) \
            VALUES (%s,%s,%s,%s,%s,%s) RETURNING id".format(schema=sysmod.schemafin())
            stmt = cur.mogrify(sql, (userid, name, ccy, valid_from, valid_to, status))
            cur.execute(stmt)
            conn.commit()
            logger.debug(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
            id = cur.fetchone()
            if id['id'] < 0: raise psycopg2.OperationalError("Account ({0}) creation fail.".format(name))
            return id['id']
    except (Exception, psycopg2.OperationalError) as err:
        logger.error(f"{__name__}.{type(err).__name__}: {err}")
        conn.rollback()
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()
    return None

# Update account
@anvil.server.callable("update_account")
@logger.log_function
def update_account(id, name, ccy, valid_from, valid_to, status):
    try:
        conn = sysmod.db_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            sql = "UPDATE {schema}.accounts SET name=%s, ccy=%s, valid_from=%s, valid_to=%s, status=%s WHERE id=%s".format(schema=sysmod.schemafin())
            stmt = cur.mogrify(sql, (name, ccy, valid_from, valid_to, status, id))
            cur.execute(stmt)
            conn.commit()
            logger.debug(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
            if cur.rowcount <= 0: raise psycopg2.OperationalError("Account ({0}) update fail.".format(name))
            return cur.rowcount
    except (Exception, psycopg2.OperationalError) as err:
        logger.error(f"{__name__}.{type(err).__name__}: {err}")
        conn.rollback()
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()
    return None

# Delete account
@anvil.server.callable("delete_account")
@logger.log_function
def delete_account(id):
    try:
        conn = sysmod.db_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            sql = "DELETE FROM {schema}.accounts WHERE id=%s".format(schema=sysmod.schemafin())
            stmt = cur.mogrify(sql, (id, ))
            cur.execute(stmt)
            conn.commit()
            logger.debug(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
            if cur.rowcount <= 0: raise psycopg2.OperationalError("Account ({0}) deletion fail.".format(name))
            return cur.rowcount
    except (Exception, psycopg2.OperationalError) as err:
        logger.error(f"{__name__}.{type(err).__name__}: {err}")
        conn.rollback()
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()
    return None

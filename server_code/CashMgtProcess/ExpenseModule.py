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
    content = list(row['abbv'] + " " + row['name'] + " (" + row['symbol'] + ")" if row['symbol'] else row['abbv'] + " " + row['name'] for row in rows)
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
    content = list(row['name'] + " (" + row['id'] + ")" for row in rows)
    return content

def create_accounts(account):
    try:
        conn = sysmod.psqldb_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            sql = "INSERT INTO {schema}.accounts (name, ccy, valid_from, valid_to, status) \
            VALUES ('{p1}','{p2}','{p3}','{p4}','{p5}') RETURNING id"
            stmt = sql.format(
                schema=sysmod.schemafin(),
                p1=account['name'],
                p2=account['ccy'],
                p3=account['valid_from'],
                p4=account['valid_to'],
                p5=True
            )
            cur.execute(stmt)
            conn.commit()
            id = cur.fetchone()
            if id['id'] < 0:
                    raise psycopg2.OperationalError("Account (id:{0}) creation fail.".format(id))
            cur.close()
        return id['id']
    except psycopg2.OperationalError as err:
        sysmod.print_data_debug("OperationalError in " + create_accounts.__name__, err)
        conn.rollback()
        cur.close()
        return None

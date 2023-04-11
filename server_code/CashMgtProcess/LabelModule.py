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
# Generate labels dropdown items
def generate_labels_dropdown():
    conn = sysmod.psqldb_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        sql = "SELECT * FROM {schema}.labels ORDER BY name ASC"
        stmt = sql.format(
            schema=sysmod.schemafin()
        )
        cur.execute(stmt)
        rows = cur.fetchall()
        cur.close()
    content = list((row['name'] + " (" + str(row['id']) + ")", [row['id'], row['name']]) for row in rows)
    return content

@anvil.server.callable
# Get selected label attributes
def get_selected_label_attr(selected_lbl):
    if selected_lbl is None or selected_lbl == '':
        return [None, None, None, True]
    else:
        conn = sysmod.psqldb_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            sql = "SELECT * FROM {schema}.labels WHERE id={p1}"   
            stmt = sql.format(
                schema=sysmod.schemafin(),
                p1=selected_lbl
            )
            cur.execute(stmt)
            row = cur.fetchone()
            cur.close()
        return [row['id'], row['name'], row['keywords'], row['status']]

@anvil.server.callable
# Create label
def create_label(name, keywords, status):
    try:
        conn = sysmod.psqldb_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            sql = "INSERT INTO {schema}.labels (name, keywords, status) \
            VALUES ('{p1}','{p2}',{p3}) RETURNING id"
            stmt = sql.format(
                schema=sysmod.schemafin(),
                p1=name,
                p2=keywords,
                p3=status
            )
            cur.execute(stmt)
            conn.commit()
            id = cur.fetchone()
            if id['id'] < 0:
                    raise psycopg2.OperationalError("Label ({0}) creation fail.".format(name))
            cur.close()
        return id['id']
    except psycopg2.OperationalError as err:
        sysmod.print_data_debug("OperationalError in " + create_label.__name__, err)
        conn.rollback()
        cur.close()
        return None

@anvil.server.callable
# Update label
def update_label(id, name, keywords, status):
    try:
        conn = sysmod.psqldb_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            sql = "UPDATE {schema}.labels SET name='{p2}', keywords='{p3}', status={p4} \
            WHERE id={p1}"
            stmt = sql.format(
                schema=sysmod.schemafin(),
                p1=id,
                p2=name,
                p3=keywords,
                p4=status
            )
            cur.execute(stmt)
            conn.commit()
            count = cur.rowcount
            if count <= 0:
                    raise psycopg2.OperationalError("Label ({0}) update fail.".format(name))
            cur.close()
        return count
    except psycopg2.OperationalError as err:
        sysmod.print_data_debug("OperationalError in " + update_label.__name__, err)
        conn.rollback()
        cur.close()
        return None

@anvil.server.callable
# Delete label
def delete_label(id):
    try:
        conn = sysmod.psqldb_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            sql = "DELETE FROM {schema}.labels WHERE id={p1}"
            stmt = sql.format(
                schema=sysmod.schemafin(),
                p1=id,
            )
            cur.execute(stmt)
            conn.commit()
            count = cur.rowcount
            if count <= 0:
                    raise psycopg2.OperationalError("Label ({0}) deletion fail.".format(name))
            cur.close()
        return count
    except psycopg2.OperationalError as err:
        sysmod.print_data_debug("OperationalError in " + delete_label.__name__, err)
        conn.rollback()
        cur.close()
        return None

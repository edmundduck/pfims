import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from . import mod_debug
from . import mod_input
from . import global_var
# Postgres impl START
import psycopg2
import psycopg2.extras
# Postgres impl END
# SQLAlchemy impl START
import sqlalchemy
from sqlalchemy import create_engine
# SQLAlchemy impl END

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

# DB table "settings" select method from Anvil DB
def anvildb_select_settings():
    row = app_tables.settings.search()
    settings = {}
    for i in row:
        settings = {
            'default_broker': i['default_broker'],
            'default_interval': i['default_interval'],
            'default_datefrom': i['default_datefrom'],
            'default_dateto': i['default_dateto']
        }
    return settings

# DB table "brokers" select method from Anvil DB
def anvildb_select_brokers():
    #broker_list = global_var.setting_broker_dropdown() + \
    #              list((''.join([r['name'], ' [', r['ccy'], ']']), r['id']) for r in app_tables.brokers.search())
    #return broker_list
    return list((''.join([r['name'], ' [', r['ccy'], ']']), r['id']) for r in app_tables.brokers.search())

# DB table "settings" update/insert method into Anvil DB
def anvildb_upsert_settings(def_broker, def_interval, def_datefrom, def_dateto):
    rows = app_tables.settings.search()
    if len(list(rows)) != 0:
        for r in rows:
            r.delete()
    app_tables.settings.add_row(
        app_uid=anvil.users.get_user()['app_uid'],
        default_broker=def_broker, 
        default_interval=def_interval, 
        default_datefrom=def_datefrom,
        default_dateto=def_dateto)

# DB table "brokers" update/insert method into Anvil DB
# NOTE: As the DB table structure is changed, this method is no longer valid
def anvildb_upsert_brokers(b_id, name, ccy):
    if b_id is None or b_id == '':
        # Generate new broker ID
        id_list = list(r['id'] for r in app_tables.brokers.search(tables.order_by('id', ascending=False)))
        if len(id_list) == 0:
            b_id = global_var.setting_broker_id_prefix() +  '1'.zfill(global_var.setting_broker_suffix_len())
        else:
            b_id = global_var.setting_broker_id_prefix() + str(int((id_list[:1][0])[2:]) + 1).zfill(global_var.setting_broker_suffix_len())
        app_tables.brokers.add_row(id=b_id, name=name, ccy=ccy)
    else:
        rows = app_tables.brokers.search(id=b_id)
        for r in rows:
            r.update(name=name, ccy=ccy)
    return b_id
      
# Return selected broker name from Anvil DB
def anvildb_get_broker_name(choice):
    result = app_tables.brokers.get(id=choice)
    return result['name'] if result is not None else ''

# Return selected broker CCY from Anvil DB
def anvildb_get_broker_ccy(choice):
    result = app_tables.brokers.get(id=choice)
    return result['ccy'] if result is not None else ''

# DB table "brokers" delete method in Anvil DB
def anvildb_delete_brokers(b_id):
    rows = app_tables.brokers.search(id=b_id)
    for r in rows:
        r.delete()    

@anvil.server.callable
# Generate SUBMITTED template selection dropdown items from Anvil DB
def anvildb_get_submitted_templ_list():
    #content = list(merge_templ_id_name(row['template_id'], row['template_name']) for row in app_tables.templates.search())
    content = list(merge_templ_id_name(row['template_id'], row['template_name']) for row in app_tables.templates.search(submitted=True))
    content.insert(0, '')
    return content

# Postgres impl START
# Establish Postgres DB connection (Yugabyte DB)
def psqldb_connect():
    connection = psycopg2.connect(
        dbname='yugabyte',
        host='europe-west2.793f25ab-3df2-4832-b84a-af6bdc81f2c7.gcp.ybdb.io',
        port='5433',
        user=anvil.secrets.get_secret('yugadb_app_usr'),
        password=anvil.secrets.get_secret('yugadb_app_pw'))
    return connection

# DB table "settings" select method from Postgres DB
def psqldb_select_settings():
    conn = psqldb_connect()
    settings = {}
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("SELECT default_broker, default_interval, default_datefrom, default_dateto FROM  " + global_var.db_schema_name() + ".settings")
        for i in cur.fetchall():
            settings = {
                'default_broker': i['default_broker'],
                'default_interval': i['default_interval'],
                'default_datefrom': i['default_datefrom'],
                'default_dateto': i['default_dateto']
            }
        cur.close()
    return settings

# DB table "brokers" select method from Postgres DB
def psgldb_select_brokers():
    conn = psqldb_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("SELECT broker_id, name, ccy FROM  " + global_var.db_schema_name() + ".brokers ORDER BY broker_id ASC")
        broker_list = cur.fetchall()
        cur.close()
    return list((''.join([r['name'], ' [', r['ccy'], ']']), r['broker_id']) for r in broker_list)

# DB table "settings" update/insert method into Postgres DB
def psgldb_upsert_settings(def_broker, def_interval, def_datefrom, def_dateto):
    conn = psqldb_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        sql = "INSERT INTO {schema}.settings (app_uid, default_broker, default_interval, default_datefrom, default_dateto) \
        VALUES ('{p1}','{p2}','{p3}'{p4}{p5}) \
        ON CONFLICT (app_uid) DO UPDATE SET default_broker='{p6}',default_interval='{p7}'{p8}{p9}"

        if def_datefrom is not None:
            datefrom1 = ",'" + str(def_datefrom) + "'"
            datefrom2 = ",default_datefrom='" + str(def_datefrom) + "'"
        else:
            datefrom1 = ",NULL"
            datefrom2 = ",default_datefrom=NULL"

        if def_dateto is not None:
            dateto1 = ",'" + str(def_dateto) + "'"
            dateto2 = ",default_dateto='" + str(def_dateto) + "'"
        else:
            dateto1 = ",NULL"
            dateto2 = ",default_dateto=NULL"

        stmt = sql.format(
            schema=global_var.db_schema_name(),
            p1=anvil.users.get_user()['app_uid'],
            p2=def_broker,
            p3=def_interval,
            p4=datefrom1,
            p5=dateto1,
            p6=def_broker,
            p7=def_interval,
            p8=datefrom2,
            p9=dateto2)

        cur.execute(stmt)
        conn.commit()
        count = cur.rowcount
        cur.close()
    return count

# DB table "brokers" update/insert method into Postgres DB
def psgldb_upsert_brokers(b_id, prefix, name, ccy):
    try:
        conn = psqldb_connect()
  
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            if b_id is None or b_id == '':
                sql = "INSERT INTO {schema}.brokers (prefix, name, ccy) VALUES ('{p1}','{p2}','{p3}') RETURNING id"
                stmt = sql.format(
                    schema=global_var.db_schema_name(),
                    p1=prefix,
                    p2=name,
                    p3=ccy)
                cur.execute(stmt)
                # broker_id (update by rule) is not updated right after INSERT INTO above, hence cannot obtain using RETURNING phrase
                id = cur.fetchone()['id']
                conn.commit()
                cur.execute("SELECT broker_id FROM  " + global_var.db_schema_name() + ".brokers WHERE id=" + str(id))
                b_id = cur.fetchone()['broker_id']
            else:
                sql1 = "UPDATE {schema}.brokers SET prefix='{p1}', name='{p2}', ccy='{p3}' WHERE broker_id='{p4}'"
                stmt = sql1.format(
                    schema=global_var.db_schema_name(),
                    p1=prefix, \
                    p2=name, \
                    p3=ccy, \
                    p4=b_id)
                cur.execute(stmt)
                conn.commit()
                count = cur.rowcount
                if count <= 0:
                    raise psycopg2.OperationalError("Update fail.")
  
            cur.close()
            return b_id
    except psycopg2.OperationalError as err:
        mod_debug.print_data_debug("OperationalError in " + psgldb_upsert_brokers.__name__, err)
        conn.rollback()
        cur.close()
        return None
      
# Return selected broker name by querying DB table "brokers" from Postgres DB
def psgldb_get_broker_name(choice):
    conn = psqldb_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("SELECT name FROM " + global_var.db_schema_name() + ".brokers WHERE broker_id='" + choice + "'")
        result = cur.fetchone()
    return result['name'] if result is not None else ''

# Return selected broker CCY by querying DB table "brokers" from Postgres DB
def psgldb_get_broker_ccy(choice):
    conn = psqldb_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("SELECT ccy FROM " + global_var.db_schema_name() + ".brokers WHERE broker_id='" + choice + "'")
        result = cur.fetchone()
    return result['ccy'] if result is not None else ''

# DB table "brokers" delete method in Postgres DB
def psgldb_delete_brokers(b_id):
    try:
        conn = psqldb_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("DELETE FROM " + global_var.db_schema_name() + ".brokers WHERE broker_id = '" + b_id + "'")
            conn.commit()
            count = cur.rowcount
            if count <= 0:
                raise psycopg2.OperationalError("Delete fail.")

            cur.close()
        return count
    except psycopg2.OperationalError as err:
        mod_debug.print_data_debug("OperationalError in " + psgldb_delete_brokers.__name__, err)
        conn.rollback()
        cur.close()
        return None

@anvil.server.callable
# Generate SUBMITTED template selection dropdown items from Postgres DB
def psgldb_get_submitted_templ_list():
    conn = psqldb_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("SELECT template_id, template_name FROM " + global_var.db_schema_name() + ".templates WHERE submitted=true")
        result = list(mod_input.merge_templ_id_name(str(row['template_id']), row['template_name']) for row in cur.fetchall())
        cur.close()
    result.insert(0, '')
    return result
        
# Postgres impl END

@anvil.server.callable
# DB table "settings" select method callable by client modules
def select_settings():
    return psqldb_select_settings()

@anvil.server.callable
# DB table "brokers" select method callable by client modules
def select_brokers():
    return psgldb_select_brokers()

@anvil.server.callable
# DB table "settings" update/insert method callable by client modules
def upsert_settings(def_broker, def_interval, def_datefrom, def_dateto):
    return psgldb_upsert_settings(def_broker, def_interval, def_datefrom, def_dateto)

@anvil.server.callable
# DB table "brokers" update/insert method callable by client modules
def upsert_brokers(b_id, name, ccy):
    return psgldb_upsert_brokers(b_id, global_var.setting_broker_id_prefix(), name, ccy)
      
@anvil.server.callable
# DB table "brokers" delete method callable by client modules
def delete_brokers(b_id):
    return psgldb_delete_brokers(b_id)
    
@anvil.server.callable
# Return selected broker name callable by client modules
def get_broker_name(choice):
    return psgldb_get_broker_name(choice)

@anvil.server.callable
# Return selected broker CCY callable by client modules
def get_broker_ccy(choice):
    return psgldb_get_broker_ccy(choice)

@anvil.server.callable
# Generate SUBMITTED template selection dropdown items
def get_submitted_templ_list():
    return psgldb_get_submitted_templ_list()

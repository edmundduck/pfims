import anvil.secrets
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import psycopg2
import psycopg2.extras
from ..Utils import Constants as const
from ..InvestmentProcess import InputModule as imod
from ..System import SystemModule as sysmod

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.

# DB table "settings" select method from Postgres DB
def psqldb_select_settings(userid):
    conn = sysmod.db_connect()
    settings = {}
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(f"SELECT default_broker, default_interval, default_datefrom, default_dateto FROM {sysmod.schemafin()}.settings")
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
    conn = sysmod.db_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(f"SELECT broker_id, name, ccy FROM {sysmod.schemafin()}.brokers ORDER BY broker_id ASC")
        broker_list = cur.fetchall()
        cur.close()
    return list((''.join([r['name'], ' [', r['ccy'], ']']), r['broker_id']) for r in broker_list)

# DB table "settings" update/insert method into Postgres DB
def psgldb_upsert_settings(userid, def_broker, def_interval, def_datefrom, def_dateto):
    try:
        conn = sysmod.db_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            sql = "INSERT INTO {schema}.settings (userid, default_broker, default_interval, default_datefrom, default_dateto) \
            VALUES ({p1},'{p2}','{p3}'{p4}{p5}) ON CONFLICT (userid) DO UPDATE SET default_broker='{p2}',default_interval='{p3}'{p6}{p7}"
            datefrom1 = ",'" + str(def_datefrom) + "'" if def_datefrom is not None else ",NULL"
            datefrom2 = ",default_datefrom='" + str(def_datefrom) + "'" if def_datefrom is not None else ",default_datefrom=NULL"
            dateto1 = ",'" + str(def_dateto) + "'" if def_dateto is not None else ",NULL"
            dateto2 = ",default_dateto='" + str(def_dateto) + "'" if def_dateto is not None else ",default_dateto=NULL"
            stmt = sql.format(
                schema=sysmod.schemafin(),
                p1=userid,
                p2=def_broker,
                p3=def_interval,
                p4=datefrom1,
                p5=dateto1,
                p6=datefrom2,
                p7=dateto2)
            cur.execute(stmt)
            conn.commit()
            if cur.rowcount <= 0: raise psycopg2.OperationalError("Update settings fail with rowcount <= 0.")
            return cur.rowcount
    except (Exception, psycopg2.OperationalError) as err:
        sysmod.print_data_debug("OperationalError in " + psgldb_upsert_settings.__name__, err)
        conn.rollback()
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()
    return None

# DB table "brokers" update/insert method into Postgres DB
def psgldb_upsert_brokers(b_id, prefix, name, ccy):
    try:
        conn = sysmod.db_connect()  
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            if b_id in (None, ''):
                cur.execute(f"INSERT INTO {sysmod.schemafin()}.brokers (prefix, name, ccy) VALUES ('{prefix}','{name}','{ccy}') RETURNING id")
                # broker_id (update by rule) is not updated right after INSERT INTO above, hence cannot obtain using RETURNING phrase
                id = cur.fetchone()['id']
                conn.commit()
                cur.execute(f"SELECT broker_id FROM {sysmod.schemafin()}.brokers WHERE id={str(id)}")
                b_id = cur.fetchone()['broker_id']
            else:
                cur.execute(f"UPDATE {sysmod.schemafin()}.brokers SET prefix='{prefix}', name='{name}', ccy='{ccy}' WHERE broker_id='{b_id}'")
                conn.commit()
                if cur.rowcount <= 0: raise psycopg2.OperationalError("Update broker fail with rowcount <= 0.")
            return b_id
    except (Exception, psycopg2.OperationalError) as err:
        sysmod.print_data_debug("OperationalError in " + psgldb_upsert_brokers.__name__, err)
        conn.rollback()
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()
    return None
      
# Return selected broker name by querying DB table "brokers" from Postgres DB
def psgldb_get_broker_name(choice):
    conn = sysmod.db_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(f"SELECT name FROM {sysmod.schemafin()}.brokers WHERE broker_id='{choice}'")
        result = cur.fetchone()
    return result['name'] if result is not None else ''

# Return selected broker CCY by querying DB table "brokers" from Postgres DB
def psgldb_get_broker_ccy(choice):
    conn = sysmod.db_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(f"SELECT ccy FROM {sysmod.schemafin()}.brokers WHERE broker_id='{choice}'")
        result = cur.fetchone()
    return result['ccy'] if result is not None else ''

# DB table "brokers" delete method in Postgres DB
def psgldb_delete_brokers(b_id):
    try:
        conn = sysmod.db_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(f"DELETE FROM {sysmod.schemafin()}.brokers WHERE broker_id = '{b_id}'")
            conn.commit()
            if cur.rowcount <= 0: raise psycopg2.OperationalError("Delete brokers fail with rowcount <= 0.")
            return cur.rowcount
    except (Exception, psycopg2.OperationalError) as err:
        sysmod.print_data_debug("OperationalError in " + psgldb_delete_brokers.__name__, err)
        conn.rollback()
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()
    return None

@anvil.server.callable
# Generate SUBMITTED template selection dropdown items from Postgres DB
def psgldb_get_submitted_templ_list():
    conn = sysmod.db_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(f"SELECT template_id, template_name FROM {sysmod.schemafin()}.templates WHERE submitted=true")
        result = list(imod.generate_template_dropdown_item(str(row['template_id']), row['template_name']) for row in cur.fetchall())
        cur.close()
    result.insert(0, '')
    return result
        
# Return search interval dropdown by querying DB table "search_interval" from Postgres DB
def psgldb_select_search_interval():
    conn = sysmod.db_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(f"SELECT * FROM {sysmod.schemarefd()}.search_interval ORDER BY seq ASC")
        rows = cur.fetchall()
        cur.close()
    return list((row['name'], row['id']) for row in rows)

# Postgres impl END

@anvil.server.callable
# DB table "settings" select method callable by client modules
def select_settings(userid):
    return psqldb_select_settings(userid)

@anvil.server.callable
# DB table "brokers" select method callable by client modules
def select_brokers():
    return psgldb_select_brokers()

@anvil.server.callable
# DB table "settings" update/insert method callable by client modules
def upsert_settings(userid, def_broker, def_interval, def_datefrom, def_dateto):
    return psgldb_upsert_settings(userid, def_broker, def_interval, def_datefrom, def_dateto)

@anvil.server.callable
# DB table "brokers" update/insert method callable by client modules
def upsert_brokers(b_id, name, ccy):
    return psgldb_upsert_brokers(b_id, const.SettingConfig.BROKER_ID_PREFIX, name, ccy)
      
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

@anvil.server.callable
# DB table "search_interval" select method callable by client modules
def select_search_interval():
    return psgldb_select_search_interval()

###################################################################
# AnvilDB access methods - Archival START

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
            b_id = const.SettingConfig.BROKER_ID_PREFIX +  '1'.zfill(const.SettingConfig.BROKER_SUFFIX_LEN)
        else:
            b_id = const.SettingConfig.BROKER_ID_PREFIX + str(int((id_list[:1][0])[2:]) + 1).zfill(const.SettingConfig.BROKER_SUFFIX_LEN)
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
    #content = list(generate_template_dropdown_item(row['template_id'], row['template_name']) for row in app_tables.templates.search())
    content = list(generate_template_dropdown_item(row['template_id'], row['template_name']) for row in app_tables.templates.search(submitted=True))
    content.insert(0, '')
    return content

# Archival END
###################################################################
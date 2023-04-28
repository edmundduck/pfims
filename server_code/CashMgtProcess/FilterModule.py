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

@anvil.server.callable
# Generate filter type dropdown items
def generate_filter_type_dropdown():
    conn = sysmod.psqldb_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        sql = f"SELECT * FROM {sysmod.schemarefd()}.filter_type ORDER BY seq ASC"
        cur.execute(sql)
        rows = cur.fetchall()
        cur.close()
    content = list((row['name'], {"id": row['id'], "text": row['name']}) for row in rows)
    return content

@anvil.server.callable
# Generate input expense table definition dropdown items
def generate_expense_tbl_def_dropdown():
    conn = sysmod.psqldb_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        sql = f"SELECT * FROM {sysmod.schemarefd()}.expense_tbl_def ORDER BY seq ASC"
        cur.execute(sql)
        rows = cur.fetchall()
        cur.close()
    content = list((row['col_name'], {"id": row['col_code'], "text": row['col_name']}) for row in rows)
    return content

@anvil.server.callable
# Generate input expense table definition dropdown items
def generate_upload_action_dropdown():
    conn = sysmod.psqldb_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        sql = f"SELECT * FROM {sysmod.schemarefd()}.upload_action ORDER BY seq ASC"
        cur.execute(sql)
        rows = cur.fetchall()
        cur.close()
    content = list((row['action'], {"id": row['id'], "text": row['action']}) for row in rows)
    return content

@anvil.server.callable
# Select the filter and rules belong to the logged on user, it can be all or particular one only
def select_filter_rules(uid, fid=None):
    conn = sysmod.psqldb_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        sql = f"SELECT a.fid, a.fname, a.flastsave, b.iid, b.action, b.extra FROM fin.filtergrp a, fin.filterrules b \
        WHERE a.fid = b.fid AND a.userid = {uid} ORDER BY a.fid ASC, b.iid ASC" if fid is None else \
        f"SELECT a.fid, a.fname, a.flastsave, b.iid, b.action, b.extra FROM fin.filtergrp a, fin.filterrules b \
        WHERE a.fid = b.fid AND a.userid = {uid} AND a.fid = {fid} ORDER BY a.fid ASC, b.iid ASC"
        cur.execute(sql)
        rows = cur.fetchall()

        result = {}
        for row in rows:
            action1, action2 = row['action'].split(",") if row['action'] is not None else [None, None]
            extra1, extra2 = row['extra'].split(",") if row['extra'] is not None else [None, None]
            if result.get(row['fid'], None) is None:
                result[row['fid']] = {
                    'fid': row['fid'],
                    'fname': row['fname'],
                    'flastsave': row['flastsave'],
                    'frules': [row['iid'], action1, action2, extra1, extra2]
                }
            else:
                r = result.get(row['fid'], None)['frules']
                r.append([row['iid'], action1, action2, extra1, extra2])
        cur.close()
    return list(result.values())

@anvil.server.callable
# Save the filter and rules
# Filter and rules ID are not generated in application side, it's handled by DB function instead, hence running SQL scripts in DB is required beforehand
def save_filter_rules(uid, fid, filter_obj):
    conn = None
    count = None
    try:
        conn = sysmod.psqldb_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            if len(filter_obj) > 0:
                # First insert/update filter group
                name = filter_obj.get('name', None)
                type_id, type = filter_obj.get('type', None).values()
                rules = filter_obj.get('rules', [])
                currenttime = datetime.now()
                if fid is not None:
                    sql = f"INSERT INTO {sysmod.schemafin()}.filtergrp (userid, fid, fname, ftype, flastsave) VALUES (%s,%s,%s,%s,%s) \
                    ON CONFLICT (fid) DO UPDATE SET fname=EXCLUDED.fname, flastsave=EXCLUDED.flastsave \
                    WHERE filtergrp.fid=EXCLUDED.fid RETURNING fid"
                    stmt = cur.mogrify(sql, (int(uid), fid, name, type_id, currenttime))
                else:
                    sql = f"INSERT INTO {sysmod.schemafin()}.filtergrp (userid, fid, fname, ftype, flastsave) VALUES (%s,DEFAULT,%s,%s,%s) RETURNING fid"
                    stmt = cur.mogrify(sql, (int(uid), name, type_id, currenttime))
                cur.execute(stmt)
                conn.commit()
                fid = (cur.fetchone())['fid']
                if fid < 0:
                    raise psycopg2.OperationalError(f"Fail to save the filter ({name}).")
            
                mogstr = []
                for rule in rules:
                    iid = int(rule[0]) if rule[0] is not None else None
                    action = f"{rule[1]},{rule[2]}"
                    extra = f"{rule[3]},{rule[4]}" if rule[3] not in (None, '') and rule[4] not in (None, '') else None
                    mogstr.append([iid, fid, action, extra])
                if len(mogstr) > 0:
                    cur.executemany(f"INSERT INTO {sysmod.schemafin()}.filterrules (iid, fid, action, extra) VALUES (%s, %s, %s, %s) \
                    ON CONFLICT (iid, fid) DO UPDATE SET \
                    action=EXCLUDED.action, \
                    extra=EXCLUDED.extra \
                    WHERE filterrules.iid=EXCLUDED.iid AND filterrules.fid=EXCLUDED.fid", mogstr)
                    conn.commit()
                    count = cur.rowcount
                    if count <= 0: raise psycopg2.OperationalError(f"Fail to save filter rules (filter name={name}).")
                    cur.close()
                else:
                    count = 0
            else:
                count = 0
    except (Exception, psycopg2.OperationalError) as err:
        sysmod.print_data_debug(f"OperationalError in {save_filter_rules.__name__}", err)
        conn.rollback()
    finally:
        if conn is not None: conn.close()        
    return {"fid": fid, "count": count}
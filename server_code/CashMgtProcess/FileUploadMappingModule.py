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
# Generate mapping dropdown items
def generate_mapping_dropdown(uid, ftype):
    conn = sysmod.psqldb_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        sql = f"SELECT * FROM {sysmod.schemafin()}.mappinggroup WHERE userid = %s AND type = %s ORDER BY fid ASC"
        stmt = cur.mogrify(sql, (uid, type, ))
        cur.execute(stmt)
        rows = cur.fetchall()
        cur.close()
    content = list((row['name'], row['id']) for row in rows)
    return content

@anvil.server.callable
# Generate mapping file type dropdown items
def generate_mapping_type_dropdown():
    conn = sysmod.psqldb_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        # TODO change filter_type to mapping_file_type
        sql = f"SELECT * FROM {sysmod.schemarefd()}.filter_type ORDER BY seq ASC"
        cur.execute(sql)
        rows = cur.fetchall()
        cur.close()
    content = list((row['name'], row['id']) for row in rows)
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
# Select the mapping and rules belong to the logged on user, it can be all or particular one only
def select_mapping_rules(uid, gid=None):
    conn = sysmod.psqldb_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        # # Filter group can have no rules so left join is required
        # sql = f"SELECT a.id, a.name, a.filetype, a.lastsave, b.datecol, b.acctcol, b.amtcol, b.remarkscol, b.stmtdtlcol, b.lblcol, b.eaction, b.etarget \
        # FROM fin.mappinggroup a LEFT JOIN fin.mappingmatrix b ON a.id = b.gid WHERE a.userid = {uid} ORDER BY a.id ASC, b.iid ASC" \
        # if fid is None else \
        # f"SELECT a.id, a.name, a.filetype, a.lastsave, b.datecol, b.acctcol, b.amtcol, b.remarkscol, b.stmtdtlcol, b.lblcol, b.eaction, b.etarget \
        # FROM fin.mappinggroup a LEFT JOIN fin.mappingmatrix b ON a.id = b.gid WHERE a.userid = {uid} AND a.id = {gid} ORDER BY a.id ASC, b.iid ASC"
        sql = f"SELECT a.id, a.name, a.filetype, a.lastsave, b.col, b.col_code, b.eaction, b.etarget, b.rule FROM fin.mappinggroup a LEFT JOIN \
        fin.mappingrules b ON a.id = b.gid WHERE a.userid = {uid} ORDER BY a.id ASC, b.col ASC" \
        if gid is None else \
        f"SELECT a.id, a.name, a.filetype, a.lastsave, b.col, b.col_code, b.eaction, b.etarget, b.rule FROM fin.mappinggroup a LEFT JOIN \
        fin.mappingrules b ON a.id = b.gid WHERE a.userid = {uid} AND a.id = {gid} ORDER BY a.id ASC, b.col ASC"
        cur.execute(sql)
        rows = cur.fetchall()

        # Group all filter rules under corresponding filter group
        result = {}
        for row in rows:
            action1 = row['col']
            action2 = row['col_code']
            extra1 = row['eaction']
            extra2 = row['etarget']
            if result.get(row['id'], None) is None:
                result[row['id']] = {
                    'id': row['id'],
                    'name': row['name'],
                    'filetype': row['filetype'],
                    'lastsave': row['lastsave'],
                    'rule': [[action1, action2, extra1, extra2]] if action1 is not None and action2 is not None else None
                }
            else:
                r = result.get(row['id'], None)['rule']
                r.append([action1, action2, extra1, extra2]) if action1 is not None and action2 is not None else r.append(None)
        cur.close()
    return list(result.values())

@anvil.server.callable
# Select the filter and rules (labels only) belong to the logged on user
def select_filter_labels_rules(fid):
    conn = sysmod.psqldb_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        # Filter group can have no rules so left join is required
        # sql = f"SELECT SUBSTRING(action, POSITION(',' IN action)-1, 1) AS col FROM fin.filterrules \
        # WHERE POSITION(',L' IN action) > 0 ORDER BY fid ASC, iid ASC" if fid is None \
        # else f"SELECT SUBSTRING(action, POSITION(',' IN action)-1, 1) AS col FROM fin.filterrules \
        # WHERE fid = {fid} AND POSITION(',L' IN action) > 0 ORDER BY fid ASC, iid ASC"
        sql = f"SELECT string_agg(SUBSTRING(action, POSITION(',' IN action)-1, 1), ',') AS col FROM fin.filterrules" if fid is None else \
        f"SELECT string_agg(SUBSTRING(action, POSITION(',' IN action)-1, 1), ',') AS col FROM fin.filterrules WHERE fid = {fid}"
        cur.execute(sql)
        row = cur.fetchone()
        cur.close()
    return row['col'] if row is not None else None

@anvil.server.callable
# Save the mapping and rules
# Mapping and rules ID are not generated in application side, it's handled by DB function instead, hence running SQL scripts in DB is required beforehand
def save_mapping_rules(uid, id, mapping_obj, del_iid=None):
    conn = None
    count = None
    dcount = None
    try:
        conn = sysmod.psqldb_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            if len(mapping_obj) > 0:
                # First insert/update filter group
                name = mapping_obj.get('name', None)
                type_id = mapping_obj.get('type', None)
                rules = mapping_obj.get('rules', [])
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

                # Second insert/update filter rules
                mogstr = []
                for rule in rules:
                    print(f"Rule:{rule}")
                    iid = int(rule[0]) if rule[0] is not None else None
                    action = f"{rule[1]},{rule[2]}"
                    extra = f"{rule[3]},{rule[4]}" if rule[3] not in (None, '') and rule[4] not in (None, '') else None
                    mogstr.append([iid, fid, action, extra])
                raise psycopg2.OperationalError(f"TERMINATE for test")
                if len(mogstr) > 0:
                    cur.executemany(f"INSERT INTO {sysmod.schemafin()}.filterrules (iid, fid, action, extra) VALUES (%s, %s, %s, %s) \
                    ON CONFLICT (iid, fid) DO UPDATE SET \
                    action=EXCLUDED.action, \
                    extra=EXCLUDED.extra \
                    WHERE filterrules.iid=EXCLUDED.iid AND filterrules.fid=EXCLUDED.fid", mogstr)
                    conn.commit()
                    count = cur.rowcount
                    if count <= 0: raise psycopg2.OperationalError(f"Fail to save filter rules (filter name={name}).")
                else:
                    count = 0
            else:
                count = 0

            # At last perform rules deletion (if any)a
            if del_iid not in (None, ''):
                args = "({0})".format(",".join(str(i) for i in del_iid))
                sql = f"DELETE FROM {sysmod.schemafin()}.filterrules WHERE fid = {fid} AND iid IN {args}"
                cur.execute(sql)
                conn.commit()
                dcount = cur.rowcount
                if dcount <= 0: raise psycopg2.OperationalError(f"Fail to save filter rules (filter name={name}).")
            else:
                dcount = 0
            cur.close()            
    except (Exception, psycopg2.OperationalError) as err:
        sysmod.print_data_debug(f"OperationalError in {save_mapping_rules.__name__}", err)
        conn.rollback()
    finally:
        if conn is not None: conn.close()        
    return {"fid": fid, "count": count, "dcount": dcount}

@anvil.server.callable
# Delete the filter
def delete_filter(uid, fid):
    conn = None
    count = None
    try:
        conn = sysmod.psqldb_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            sql = f"DELETE FROM {sysmod.schemafin()}.filtergrp WHERE userid = {uid} AND fid = {fid}"
            cur.execute(sql)
            conn.commit()
            count = cur.rowcount
            if count <= 0:
                raise psycopg2.OperationalError(f"Filter (id:{fid}) deletion fail.")
            cur.close()
    except (Exception, psycopg2.OperationalError) as err:
        sysmod.print_data_debug(f"OperationalError in {delete_filter.__name__}", err)
        conn.rollback()
    finally:
        if conn is not None: conn.close()        
    return count
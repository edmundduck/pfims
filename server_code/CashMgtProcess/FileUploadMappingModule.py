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
def generate_mapping_dropdown(ftype):
    userid = sysmod.get_current_userid()
    conn = sysmod.db_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        sql = f"SELECT * FROM {sysmod.schemafin()}.mappinggroup WHERE userid = %s AND filetype = %s ORDER BY id ASC"
        stmt = cur.mogrify(sql, (userid, ftype, ))
        cur.execute(stmt)
        rows = cur.fetchall()
        cur.close()
    content = list((row['name'], row['id']) for row in rows)
    return content

@anvil.server.callable
# Generate mapping file type dropdown items
def generate_mapping_type_dropdown():
    conn = sysmod.db_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        # TODO change filter_type to mapping_file_type
        sql = f"SELECT * FROM {sysmod.schemarefd()}.filter_type ORDER BY seq ASC"
        cur.execute(sql)
        rows = cur.fetchall()
        cur.close()
    content = list((row['name'], [row['id'], row['name']]) for row in rows)
    return content

@anvil.server.callable
# Generate input expense table definition dropdown items
def generate_expense_tbl_def_dropdown():
    conn = sysmod.db_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        sql = f"SELECT * FROM {sysmod.schemarefd()}.expense_tbl_def ORDER BY seq ASC"
        cur.execute(sql)
        rows = cur.fetchall()
        cur.close()
    content = list((row['col_name'], [row['col_code'], row['col_name']]) for row in rows)
    return content

@anvil.server.callable
# Generate input expense table definition dropdown items
def generate_upload_action_dropdown():
    conn = sysmod.db_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        sql = f"SELECT * FROM {sysmod.schemarefd()}.upload_action ORDER BY seq ASC"
        cur.execute(sql)
        rows = cur.fetchall()
        cur.close()
    content = list((row['action'], [row['id'], row['action']]) for row in rows)
    return content

# Generate the whole mapping matrix to be used by Pandas columns combination based on mapping rules
def generate_mapping_matrix(matrix, col_def):
    if len(col_def) < 1:
        return [[]]
    col_val = matrix.get(col_def.pop(0))
    r = generate_mapping_matrix(matrix, col_def)
    result = None
    for ri in r:
        if len(col_val) > 0:
            for i in col_val:
                # Duplicate result according to filter param size
                y = ri.copy()
                # TODO - the column sequence has to be fixed as matrixstr is stored in list instead of object
                y.insert(0, i)
                result = [y] + result if result is not None else [y]
        else:
            # Duplicate result according to filter param size
            y = ri.copy()
            # TODO - the column sequence has to be fixed as matrixstr is stored in list instead of object
            y.insert(0, '')
            result = [y] + result if result is not None else [y]
    if result is None: result = r
    return result

# Select input expense table definition column ID
def select_expense_tbl_def_id():
    conn = sysmod.db_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        sql = f"SELECT * FROM {sysmod.schemarefd()}.expense_tbl_def ORDER BY seq ASC"
        cur.execute(sql)
        rows = cur.fetchall()
        cur.close()
    content = list(row['col_code'] for row in rows)
    return content

@anvil.server.callable
# Select the mapping and rules belong to the logged on user, it can be all or particular one only
def select_mapping_rules(gid=None):
    userid = sysmod.get_current_userid()
    conn = sysmod.db_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        # Mapping group can have no rules so left join is required
        sql = f"SELECT a.id, a.name, a.filetype, a.lastsave, b.col, b.col_code, b.eaction, b.etarget, b.rule FROM fin.mappinggroup a LEFT JOIN \
        fin.mappingrules b ON a.id = b.gid WHERE a.userid = {userid} ORDER BY a.id ASC, b.col ASC" \
        if gid is None else \
        f"SELECT a.id, a.name, a.filetype, a.lastsave, b.col, b.col_code, b.eaction, b.etarget, b.rule FROM fin.mappinggroup a LEFT JOIN \
        fin.mappingrules b ON a.id = b.gid WHERE a.userid = {userid} AND a.id = {gid} ORDER BY a.id ASC, b.col ASC"
        cur.execute(sql)
        rows = cur.fetchall()

        # Group all mapping rules under corresponding mapping group
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
# Select the mapping matrix belong to the logged on user
def select_mapping_matrix(id):
    conn = sysmod.db_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        sql = f"SELECT datecol AS trandate, acctcol AS account_id, amtcol AS amount, remarkscol AS remarks, stmtdtlcol AS stmt_dtl, lblcol AS labels \
        FROM {sysmod.schemafin()}.mappingmatrix WHERE gid = {id}"
        cur.execute(sql)
        rows = cur.fetchall()
        cur.close()
    return rows

@anvil.server.callable
# Save the mapping and rules
# Mapping and rules ID are not generated in application side, it's handled by DB function instead, hence running SQL scripts in DB is required beforehand
def save_mapping_rules(id, mapping_rules, del_iid=None):
    conn = None
    count = None
    dcount = None
    userid = sysmod.get_current_userid()
    try:
        conn = sysmod.db_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            if len(mapping_rules) > 0:
                # First insert/update mapping group
                name = mapping_rules.get('name', None)
                type_id = mapping_rules.get('filetype', None)
                rules = mapping_rules.get('rules', [])
                currenttime = datetime.now()
                if id is not None:
                    sql = f"INSERT INTO {sysmod.schemafin()}.mappinggroup (userid, id, name, filetype, lastsave) VALUES (%s,%s,%s,%s,%s) \
                    ON CONFLICT (id) DO UPDATE SET name=EXCLUDED.name, filetype=EXCLUDED.filetype, lastsave=EXCLUDED.lastsave WHERE mappinggroup.id=EXCLUDED.id RETURNING id"
                    stmt = cur.mogrify(sql, (int(userid), id, name, type_id, currenttime))
                else:
                    sql = f"INSERT INTO {sysmod.schemafin()}.mappinggroup (userid, id, name, filetype, lastsave) VALUES (%s,DEFAULT,%s,%s,%s) RETURNING id"
                    stmt = cur.mogrify(sql, (int(userid), name, type_id, currenttime))
                cur.execute(stmt)
                conn.commit()
                id = (cur.fetchone())['id']
                if id < 0:
                    raise psycopg2.OperationalError(f"Fail to save the mapping ({name}).")

                # Second insert/update mapping rules
                mogstr = []
                # For later on the mapping matrix 
                matrixobj = {}
                tbl_def = select_expense_tbl_def_id()
                for c in tbl_def:
                    matrixobj[c] = []
                for rule in rules:
                    col_id = f"{rule[0]}"
                    column = f"{rule[1]}"
                    eaction = f"{rule[2]}" if rule[2] not in (None, '') else None
                    etarget = f"{rule[3]}" if rule[2] not in (None, '') and rule[3] not in (None, '') else None
                    rule = f"{rule[4]}"
                    mogstr.append([id, col_id, column, eaction, etarget, rule])
                    matrixobj[column].append(col_id)
                if len(mogstr) > 0:
                    cur.executemany(f"INSERT INTO {sysmod.schemafin()}.mappingrules (gid, col, col_code, eaction, etarget, rule) VALUES \
                    (%s, %s, %s, %s, %s, %s) ON CONFLICT (gid, col) DO UPDATE SET col_code=EXCLUDED.col_code, eaction=EXCLUDED.eaction, \
                    etarget=EXCLUDED.etarget, rule=EXCLUDED.rule WHERE mappingrules.gid=EXCLUDED.gid AND mappingrules.col=EXCLUDED.col", mogstr)
                    conn.commit()
                    count = cur.rowcount
                    if count <= 0: raise psycopg2.OperationalError(f"Fail to save mapping rules (Mapping name={name}).")
                else:
                    count = 0

                # Third insert/update mapping matrix
                matrixstr = generate_mapping_matrix(matrixobj, tbl_def)
                if len(matrixstr) > 0:
                    cur.execute(f"DELETE FROM {sysmod.schemafin()}.mappingmatrix WHERE gid = {id}")
                    conn.commit()
                    dcount = cur.rowcount

                    # TODO - the column sequence has to be fixed as matrixstr is stored in list instead of object
                    cur.executemany(f"INSERT INTO {sysmod.schemafin()}.mappingmatrix (gid, datecol, acctcol, amtcol, lblcol, remarkscol, stmtdtlcol) \
                    VALUES ({id}, %s, %s, %s, %s, %s, %s)", matrixstr)
                    conn.commit()
                    count = cur.rowcount
                    if count <= 0 or dcount < 0: raise psycopg2.OperationalError(f"Fail to save mapping matrix (Mapping name={name}).")
            else:
                count = 0

            # At last perform rules deletion (if any)
            if del_iid not in (None, ''):
                args = "({0})".format(",".join(f"'{i}'" for i in del_iid))
                sql = f"DELETE FROM {sysmod.schemafin()}.mappingrules WHERE gid = {id} AND col IN {args}"
                cur.execute(sql)
                conn.commit()
                dcount = cur.rowcount
                if dcount <= 0: raise psycopg2.OperationalError(f"Fail to remove deleted mapping rules (Mapping name={name}).")
            else:
                dcount = 0
            cur.close()            
    except (Exception, psycopg2.OperationalError) as err:
        sysmod.print_data_debug(f"OperationalError in {save_mapping_rules.__name__}", err)
        conn.rollback()
    finally:
        if conn is not None: conn.close()        
    return {"id": id, "count": count, "dcount": dcount}

@anvil.server.callable
def select_mapping_extra_actions(id):
    conn = sysmod.db_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        # Mapping group can have no rules so left join is required
        # TODO in progress
        sql = f"SELECT col, col_code, eaction, etarget FROM fin.mappingrules WHERE gid = {id} AND eaction is not NULL"
        cur.execute(sql)
        rows = cur.fetchall()
        cur.close()
    return list(rows)

@anvil.server.callable
# Delete mapping and its associated rules and matrix
def delete_mapping(id):
    try:
        conn = sysmod.db_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(f"DELETE FROM {sysmod.schemafin()}.mappinggroup WHERE id = '{id}'")
            conn.commit()
            if cur.rowcount <= 0: raise psycopg2.OperationalError("Delete mapping group fail with rowcount <= 0.")
            return cur.rowcount
    except (Exception, psycopg2.OperationalError) as err:
        sysmod.print_data_debug("OperationalError in " + delete_mapping.__name__, err)
        conn.rollback()
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()
    return None

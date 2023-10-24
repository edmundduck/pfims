import anvil.server
import psycopg2
import psycopg2.extras
from datetime import date, datetime
from ..SysProcess import SystemModule as sysmod
from ..SysProcess import LoggingModule
from ..Utils import Helper
from ..Utils.Constants import Database

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.

logger = LoggingModule.ServerLogger()

@anvil.server.callable("generate_mapping_list")
@logger.log_function
def generate_mapping_list(ftype):
    """
    Select mapping groups from the mapping group DB table for data mapping logic based on selected file type.

    Parameters:
        ftype (string): The selected file type for corresponding mapping groups.
    
    Returns:
        rows (list of RealDictRow): A list of mapping groups based on selected file type.
    """
    conn = sysmod.db_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        sql = "SELECT * FROM {schema}.mappinggroup WHERE userid = %s AND filetype = %s ORDER BY id ASC".format(
            schema=Database.SCHEMA_FIN
        )
        stmt = cur.mogrify(sql, (userid, ftype, ))
        cur.execute(stmt)
        rows = cur.fetchall()
        logger.trace("rows=", rows)
        cur.close()
        return rows

@anvil.server.callable("generate_mapping_type_list")
@logger.log_function
def generate_mapping_type_list():
    """
    Select mapping file types from the import file DB table.

    Returns:
        rows (list of RealDictRow): A list of import file types.
    """
    conn = sysmod.db_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        sql = "SELECT * FROM {schema}.import_filetype ORDER BY seq ASC".format(
            schema=Database.SCHEMA_REFDATA
        )
        cur.execute(sql)
        rows = cur.fetchall()
        logger.trace("rows=", rows)
        cur.close()
        return rows

@anvil.server.callable("generate_expense_tbl_def_list")
@logger.log_function
def generate_expense_tbl_def_list():
    """
    Select expense table definition of each column type from the expense table definition DB table.

    Returns:
        rows (list of RealDictRow): A list of column types.
    """
    conn = sysmod.db_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        sql = "SELECT * FROM {schema}.expense_tbl_def ORDER BY seq ASC".format(
            schema=Database.SCHEMA_REFDATA
        )
        cur.execute(sql)
        rows = cur.fetchall()
        cur.close()
        return rows

@anvil.server.callable("generate_upload_action_list")
@logger.log_function
def generate_upload_action_list():
    """
    Select import file upload action data from the import file upload action DB table.

    Returns:
        rows (list of RealDictRow): A list of upload actions.
    """
    conn = sysmod.db_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        sql = "SELECT * FROM {schema}.upload_action ORDER BY seq ASC".format(
            schema=Database.SCHEMA_REFDATA
        )
        cur.execute(sql)
        rows = cur.fetchall()
        cur.close()
        return rows

@anvil.server.callable("select_mapping_rules")
@logger.log_function
def select_mapping_rules(gid=None):
    """
    Select the mapping and rules belong to the logged on user, it can be all or particular one only.

    Parameters:
        gid (int): The ID of the mapping group.

    Returns:
        result (list of dict): The merged data of both mapping rules and mapping groups grouped by mapping group ID.
    """
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
        logger.trace("rows=", rows)

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
        logger.trace("result=", result)
        cur.close()
    return list(result.values())

@anvil.server.callable("select_mapping_matrix")
@logger.log_function
def select_mapping_matrix(id):
    """
    Select the mapping matrix belong to the logged on user.

    Parameters:
        id (int): The group ID of the mapping matrix, which also equal to the ID of the corresponding mapping group.

    Returns:
        rows (list of dict): All the mapping matrix which belongs to the logged on user.
    """
    from ..Entities.ExpenseTransaction import ExpenseTransaction
    conn = sysmod.db_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        sql = f"SELECT datecol AS {ExpenseTransaction.field_date()}, acctcol AS {ExpenseTransaction.field_account()}, amtcol AS {ExpenseTransaction.field_amount()}, remarkscol AS {ExpenseTransaction.field_remarks()}, \
        stmtdtlcol AS {ExpenseTransaction.field_statement_detail()}, lblcol AS {ExpenseTransaction.field_labels()} FROM {Database.SCHEMA_FIN}.mappingmatrix WHERE gid = {id}"
        cur.execute(sql)
        rows = cur.fetchall()
        # Special handling to make keys found in expense_tbl_def all in upper case to match with client UI, server and DB definition
        # Without this the repeating panel can display none of the data returned from DB as the keys case from dict are somehow auto-lowered
        rows = Helper.upper_dict_keys(rows, ExpenseTransaction.get_data_transform_definition())
        cur.close()
    return rows

@logger.log_function
def save_mapping_group(id, mogstr_group):
    """
    Save the mapping group into the DB table.

    Mapping and rules ID are not generated in application side, it's handled by DB function instead, hence running SQL scripts in DB is required beforehand.

    Parameters:
        mogstr_group (string): Mogrified string for mapping group SQL.

    Returns:
        id (int): The mapping group ID.
    """
    userid = sysmod.get_current_userid()
    conn = sysmod.db_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        try:
            # First insert/update mapping group
            if id:
                sql = "INSERT INTO {schema}.mappinggroup (userid, id, name, filetype, lastsave) VALUES (%s,%s,%s,%s,%s) ON CONFLICT (id) DO UPDATE SET \
                name=EXCLUDED.name, filetype=EXCLUDED.filetype, lastsave=EXCLUDED.lastsave WHERE mappinggroup.id=EXCLUDED.id RETURNING id".format(
                    schema=Database.SCHEMA_FIN
                )
            else:
                sql = "INSERT INTO {schema}.mappinggroup (userid, id, name, filetype, lastsave) VALUES (%s,DEFAULT,%s,%s,%s) RETURNING id".format(
                    schema=Database.SCHEMA_FIN
                )
            stmt = cur.mogrify(sql, mogstr_group)
            cur.execute(stmt)
            conn.commit()
            result = cur.fetchone()
            if result:
                id = result.get('id')
            else:
                raise psycopg2.OperationalError("Fail to update mapping group with ID. Aborting further update.")
        except psycopg2.OperationalError as err:
            logger.error(err)
            conn.rollback()
            raise psycopg2.OperationalError(err)
        finally:
            if cur is not None: cur.close()
            if conn is not None: conn.close()        
        return id

@logger.log_function
def save_mapping_rules_n_matrix(id, mogstr_rules, mogstr_matrix, mogstr_delete):
    """
    Save the mapping rules and matrix into the DB table.

    Mapping and rules ID are not generated in application side, it's handled by DB function instead, hence running SQL scripts in DB is required beforehand.

    Parameters:
        mogstr_rules (string): Mogrified string for mapping rules SQL.
        mogstr_matrix (string): Mogrified string for mapping matrix SQL.
        mogstr_delete (string): Mogrified string for mapping rules deletion SQL.
    """
    conn = None
    try:
        userid = sysmod.get_current_userid()
        conn = sysmod.db_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            # Second insert/update mapping rules
            if len(mogstr_rules) > 0:
                sql = "INSERT INTO {schema}.mappingrules (gid, col, col_code, eaction, etarget, rule) VALUES \
                (%s, %s, %s, %s, %s, %s) ON CONFLICT (gid, col) DO UPDATE SET col_code=EXCLUDED.col_code, eaction=EXCLUDED.eaction, \
                etarget=EXCLUDED.etarget, rule=EXCLUDED.rule WHERE mappingrules.gid=EXCLUDED.gid AND mappingrules.col=EXCLUDED.col".format(
                    schema=Database.SCHEMA_FIN
                )
                cur.executemany(sql, mogstr_rules)

            # Third insert/update mapping matrix
            if len(mogstr_matrix) > 0:
                sql = "DELETE FROM {schema}.mappingmatrix WHERE gid = %s".format(
                    schema=Database.SCHEMA_FIN
                )
                stmt = cur.mogrify(sql, (id, ))
                cur.execute(stmt)

                sql = "INSERT INTO {schema}.mappingmatrix (gid, datecol, acctcol, amtcol, lblcol, remarkscol, stmtdtlcol) \
                VALUES ({id}, %s, %s, %s, %s, %s, %s)".format(
                    schema=Database.SCHEMA_FIN,
                    id=id
                )
                cur.executemany(sql, mogstr_matrix)

            # At last perform rules deletion (if any)
            if mogstr_delete:
                sql = "DELETE FROM {schema}.mappingrules WHERE gid = %s AND col IN %s".format(
                    schema=Database.SCHEMA_FIN
                )
                stmt = cur.mogrify(sql, (id, mogstr_delete))
                cur.execute(stmt)

            # Reconciliation
            sql = "SELECT g.userid, g.id, g.name, g.filetype, m.datecol, m.acctcol, m.amtcol, m.remarkscol, m.stmtdtlcol, m.lblcol FROM \
            {schema}.mappinggroup g LEFT JOIN fin.mappingmatrix m ON g.id = m.gid WHERE g.id = %s".format(
                schema=Database.SCHEMA_FIN
            )
            stmt = cur.mogrify(sql, (id, ))
            cur.execute(stmt)
            conn.commit()
            rows = cur.fetchall()
            if len(rows) != len(mogstr_matrix): raise psycopg2.OperationalError("Row counts returned don't match with the input. Please reenter the mapping detail.")
            return len(rows)
    except psycopg2.OperationalError as err:
        logger.error(err)
        conn.rollback()
        raise psycopg2.OperationalError(err)
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()        
    return None

@anvil.server.callable("select_mapping_extra_actions")
@logger.log_function
def select_mapping_extra_actions(id):
    """
    Select the extra mapping actions from mapping rules.

    Parameters:
        id (int): The group ID of the mapping matrix, which also equal to the ID of the corresponding mapping group.

    Returns:
        rows (list): The list of column, column code, extra action and extra action target.
    """
    conn = sysmod.db_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        # Mapping group can have no rules so left join is required
        sql = "SELECT col, col_code, eaction, etarget FROM fin.mappingrules WHERE gid = %s AND eaction is not NULL"
        stmt = cur.mogrify(sql, (id, ))
        cur.execute(stmt)
        rows = cur.fetchall()
        cur.close()
    return list(rows)

@anvil.server.callable("delete_mapping")
@logger.log_function
def delete_mapping(id):
    """
    Delete mapping group and its associated rules and matrix.

    Parameters:
        id (int): The ID of the mapping group.

    Returns:
        cur.rowcount (int): Successful delete row count, otherwise None.
    """
    try:
        conn = sysmod.db_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            sql = "DELETE FROM {schema}.mappinggroup WHERE id = %s".format(
                schema=Database.SCHEMA_FIN
            )
            stmt = cur.mogrify(sql, (id, ))
            cur.execute(stmt)
            conn.commit()
            logger.debug(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
            if cur.rowcount <= 0: raise psycopg2.OperationalError("Delete mapping group fail with rowcount <= 0.")
            return cur.rowcount
    except psycopg2.OperationalError as err:
        logger.error(err)
        conn.rollback()
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()
    return None

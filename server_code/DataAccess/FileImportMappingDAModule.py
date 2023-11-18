import anvil.server
import psycopg2
import psycopg2.extras
from datetime import date, datetime
from .. import SystemProcess as sys
from ..ServerUtils.LoggingModule import ServerLogger
from ..Utils import Helper
from ..Utils.Constants import Database

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.

logger = ServerLogger()

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
    userid = sys.get_current_userid()
    conn = sys.db_connect()
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
    conn = sys.db_connect()
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
    conn = sys.db_connect()
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
    conn = sys.db_connect()
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
    userid = sys.get_current_userid()
    conn = sys.db_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        # Mapping group can have no rules so left join is required
        sql = f"SELECT a.id, a.name, a.filetype, a.lastsave, a.description, b.col, b.col_code, b.eaction, b.etarget, b.rule FROM fin.mappinggroup a LEFT JOIN \
        fin.mappingrules b ON a.id = b.gid WHERE a.userid = {userid} ORDER BY a.id ASC, b.col ASC" \
        if gid is None else \
        f"SELECT a.id, a.name, a.filetype, a.lastsave, a.description, b.col, b.col_code, b.eaction, b.etarget, b.rule FROM fin.mappinggroup a LEFT JOIN \
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
                    'description': row['description'],
                    'rule': [[action1, action2, extra1, extra2]] if action1 is not None and action2 is not None else None
                }
            else:
                r = result.get(row['id'], None)['rule']
                r.append([action1, action2, extra1, extra2]) if action1 is not None and action2 is not None else r.append(None)
        logger.trace("result=", result)
        cur.close()
    return list(result.values())

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
    conn = sys.db_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        sql = "SELECT datecol AS {datecol}, acctcol AS {acctcol}, amtcol AS {amtcol}, remarkscol AS {remarkscol}, stmtdtlcol AS {stmtdtlcol}, lblcol AS {lblcol} \
        FROM {schema}.mappingmatrix WHERE gid = %s".format(
            datecol=ExpenseTransaction.field_date(),
            acctcol=ExpenseTransaction.field_account(),
            amtcol=ExpenseTransaction.field_amount(),
            remarkscol=ExpenseTransaction.field_remarks(),
            stmtdtlcol=ExpenseTransaction.field_statement_detail(),
            lblcol=ExpenseTransaction.field_labels(),
            schema=Database.SCHEMA_FIN
        )
        stmt = cur.mogrify(sql, (id, ))
        cur.execute(stmt)
        rows = cur.fetchall()
        # Special handling to make keys found in expense_tbl_def all in upper case to match with client UI, server and DB definition
        # Without this the repeating panel can display none of the data returned from DB as the keys case from dict are somehow auto-lowered
        rows = Helper.upper_dict_keys(rows, ExpenseTransaction.get_data_transform_definition())
        cur.close()
        return rows

@logger.log_function
def save_mapping_group(import_grp):
    """
    Save the mapping group into the DB table.

    Mapping and rules ID are not generated in application side, it's handled by DB function instead, hence running SQL scripts in DB is required beforehand.

    Parameters:
        import_grp (ImportMappingGroup): The import mapping group object containing all group and rules detail.

    Returns:
        id (int): The mapping group ID.
    """
    conn = sys.db_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        try:
            # First insert/update mapping group
            if import_grp.get_id():
                sql = "INSERT INTO {schema}.mappinggroup (userid, id, name, filetype, lastsave, description) VALUES (%s,%s,%s,%s,%s,%s) ON CONFLICT (id) DO UPDATE SET \
                name=EXCLUDED.name, filetype=EXCLUDED.filetype, lastsave=EXCLUDED.lastsave, description=EXCLUDED.description WHERE mappinggroup.id=EXCLUDED.id RETURNING id".format(
                    schema=Database.SCHEMA_FIN
                )
                stmt = cur.mogrify(sql, (import_grp.get_user_id(), import_grp.get_id(), import_grp.get_name(), import_grp.get_file_type(), import_grp.get_lastsaved_time(), import_grp.get_description()))
            else:
                sql = "INSERT INTO {schema}.mappinggroup (userid, id, name, filetype, lastsave, description) VALUES (%s,DEFAULT,%s,%s,%s,%s) RETURNING id".format(
                    schema=Database.SCHEMA_FIN
                )
                stmt = cur.mogrify(sql, (import_grp.get_user_id(), import_grp.get_name(), import_grp.get_file_type(), import_grp.get_lastsaved_time(), import_grp.get_description()))
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
def save_mapping_rules_n_matrix(id, mogstr_rules, mogstr_matrix, del_iid):
    """
    Save the mapping rules and matrix into the DB table.

    Mapping and rules ID are not generated in application side, it's handled by DB function instead, hence running SQL scripts in DB is required beforehand.

    Parameters:
        mogstr_rules (string): Mogrified string for mapping rules SQL.
        mogstr_matrix (string): Mogrified string for mapping matrix SQL.
        del_iid (string): The string of IID concatenated by comma to be deleted
    """
    conn = sys.db_connect()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        try:
            # Second insert/update mapping rules
            if len(mogstr_rules) > 0:
                sql1 = "INSERT INTO {schema}.mappingrules (gid, col, col_code, eaction, etarget, rule) VALUES \
                (%s, %s, %s, %s, %s, %s) ON CONFLICT (gid, col) DO UPDATE SET col_code=EXCLUDED.col_code, eaction=EXCLUDED.eaction, \
                etarget=EXCLUDED.etarget, rule=EXCLUDED.rule WHERE mappingrules.gid=EXCLUDED.gid AND mappingrules.col=EXCLUDED.col".format(
                    schema=Database.SCHEMA_FIN
                )
                cur.executemany(sql1, mogstr_rules)

            # Third insert/update mapping matrix
            if len(mogstr_matrix) > 0:
                sql2 = "DELETE FROM {schema}.mappingmatrix WHERE gid = %s".format(
                    schema=Database.SCHEMA_FIN
                )
                stmt2 = cur.mogrify(sql2, (id, ))
                cur.execute(stmt2)

                sql3 = "INSERT INTO {schema}.mappingmatrix (gid, datecol, acctcol, amtcol, lblcol, remarkscol, stmtdtlcol) \
                VALUES ({id}, %s, %s, %s, %s, %s, %s)".format(
                    schema=Database.SCHEMA_FIN,
                    id=id
                )
                cur.executemany(sql3, mogstr_matrix)

            # At last perform rules deletion (if any)
            if del_iid:
                mogstr_delete = ','.join(cur.mogrify("%s", (d, )).decode('utf-8') for d in del_iid)
                logger.trace('mogstr_delete=', mogstr_delete)
                sql4 = "DELETE FROM {schema}.mappingrules WHERE gid = {gid} AND col IN ({iid})".format(
                    schema=Database.SCHEMA_FIN,
                    gid=id,
                    iid=mogstr_delete
                )
                cur.execute(sql4)

            # Reconciliation
            sql5 = "SELECT g.userid, g.id, g.name, g.filetype, m.datecol, m.acctcol, m.amtcol, m.remarkscol, m.stmtdtlcol, m.lblcol FROM \
            {schema}.mappinggroup g LEFT JOIN fin.mappingmatrix m ON g.id = m.gid WHERE g.id = %s".format(
                schema=Database.SCHEMA_FIN
            )
            stmt5 = cur.mogrify(sql5, (id, ))
            cur.execute(stmt5)
            conn.commit()
            rows = cur.fetchall()
            logger.debug(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
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

@logger.log_function
def select_mapping_extra_actions(id):
    """
    Select the extra mapping actions from mapping rules.

    Parameters:
        id (int): The group ID of the mapping matrix, which also equal to the ID of the corresponding mapping group.

    Returns:
        rows (list): The list of column, column code, extra action and extra action target.
    """
    conn = sys.db_connect()
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
        conn = sys.db_connect()
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

from ..CashMgtProcess import FileUploadMappingModule
from ..Utils import Helper

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.

@logger.log_function
def generate_mapping_matrix(matrix, col_def):
    """
    Generate the whole mapping matrix to be used by Pandas columns combination based on mapping rules.

    Examples as follow,
    matrix= {'D': ['A', 'L'], 'AC': ['D'], 'AM': ['C', 'K'], 'L': ['E'], 'R': ['B'], 'SD': []}
    col_def= ['D', 'AC', 'AM', 'L', 'R', 'SD']
    result= [{'DTE': 'J', 'ACC': '', 'AMT': 'C', 'RMK': 'H', 'STD': '', 'LBL': 'B'}, {'DTE': 'J', 'ACC': '', 'AMT': 'F', 'RMK': 'H', 'STD': '', 'LBL': 'B'}]

    Parameters:
        matrix (dict of list): The matrix of Excel column ID and column type mapping.
        col_def (list): The column type definition.

    Returns:
        result (list of dict): The matrix of all Excel column ID combinations under the single column type definition (each column type occurs only onces).
    """
    logger.debug("matrix=", matrix)
    logger.debug("col_def=", col_def)
    if len(col_def) < 1:
        return [[]]
    col_val = matrix.get(col_def.pop(0))
    r = generate_mapping_matrix(matrix, col_def)
    result = None
    for ri in r:
        if col_val is not None and len(col_val) > 0:
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
    logger.trace("result=", result)
    return result

@anvil.server.callable("save_import_mapping")
@logger.log_function
def save_import_mapping(id, name, filetype_id, rules, mapping_rules, del_iid=None):
    """
    Process data for updating import mapping data.

    Parameters:
        id (int): The ID of the mapping group.
        name (string): The mapping group name.
        filetype (list): The selected filetype ID.
        rules (list): The list of criteria of the rule to be saved.
        del_iid (string): The string of IID concatenated by comma to be deleted

    Returns:
        dict: Includes mapping group ID; successful insert/update row count (count), otherwise None; and successful delete row count (dcount), otherwise None.
    """

    currenttime = datetime.now()

    # Prepare data for mappinggroup
    mgroup = (int(userid), id, name, filetype_id, currenttime) if id else (int(userid), name, filetype_id, currenttime)

    mrules = []
    matrixobj = {}
    for rule in rules:
        mrules.append([id, rule[0], rule[1], rule[2], rule[3] if rule[2] and rule[3] else None, rule[4]])
        matrixobj[rule[1]] = matrixobj[rule[1]] + [rule[0]] if matrixobj[rule[1]] else [rule[0]]
    
    tbl_def_dict = Helper.to_dict_of_list(FileUploadMappingModule.generate_expense_tbl_def_list())
    mmatrix = generate_mapping_matrix(matrixobj, tbl_def_dict.get('col_code'))
    # args = "({0})".format(",".join(f"'{i}'" for i in del_iid))
    try:
        conn = sysmod.db_connect()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            # First insert/update mapping group
            currenttime = datetime.now()
            if id is not None:
                sql = f"INSERT INTO {Database.SCHEMA_FIN}.mappinggroup (userid, id, name, filetype, lastsave) VALUES (%s,%s,%s,%s,%s) \
                ON CONFLICT (id) DO UPDATE SET name=EXCLUDED.name, filetype=EXCLUDED.filetype, lastsave=EXCLUDED.lastsave WHERE mappinggroup.id=EXCLUDED.id RETURNING id"
                stmt = cur.mogrify(sql, (int(userid), id, name, filetype_id, currenttime))
            else:
                sql = f"INSERT INTO {Database.SCHEMA_FIN}.mappinggroup (userid, id, name, filetype, lastsave) VALUES (%s,DEFAULT,%s,%s,%s) RETURNING id"
                stmt = cur.mogrify(sql, (int(userid), name, filetype_id, currenttime))
            cur.execute(stmt)
            conn.commit()
            logger.debug(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
            id = (cur.fetchone())['id']
            if id < 0:
                raise psycopg2.OperationalError(f"Fail to save the mapping ({name}).")

            # Second insert/update mapping rules
            mogstr_rules = []
            # For later on the mapping matrix 
            matrixobj = {}
            tbl_def = select_expense_tbl_def_id()
            for rule in rules:
                mogstr_rules.append([id, rule[0], rule[1], rule[2], rule[3] if rule[2] and rule[3] else None, rule[4]])
                matrixobj[column] = matrixobj[column] + [rule[0]] if matrixobj[column] else [rule[0]]
            logger.trace("matrixobj=", matrixobj)
            if len(mogstr) > 0:
                cur.executemany(f"INSERT INTO {Database.SCHEMA_FIN}.mappingrules (gid, col, col_code, eaction, etarget, rule) VALUES \
                (%s, %s, %s, %s, %s, %s) ON CONFLICT (gid, col) DO UPDATE SET col_code=EXCLUDED.col_code, eaction=EXCLUDED.eaction, \
                etarget=EXCLUDED.etarget, rule=EXCLUDED.rule WHERE mappingrules.gid=EXCLUDED.gid AND mappingrules.col=EXCLUDED.col", mogstr_rules)
                conn.commit()
                count = cur.rowcount
                logger.debug(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
                if count <= 0: raise psycopg2.OperationalError(f"Fail to save mapping rules (Mapping name={name}).")
            else:
                count = 0

            # Third insert/update mapping matrix
            matrixstr = generate_mapping_matrix(matrixobj, tbl_def)
            if len(matrixstr) > 0:
                sql = "DELETE FROM {schema}.mappingmatrix WHERE gid = %s".format(
                    schema=Database.SCHEMA_FIN
                )
                stmt = cur.mogrify(sql, (id, ))
                cur.execute(stmt)
                conn.commit()
                dcount = cur.rowcount

                # TODO - the column sequence has to be fixed as matrixstr is stored in list instead of object
                cur.executemany(f"INSERT INTO {Database.SCHEMA_FIN}.mappingmatrix (gid, datecol, acctcol, amtcol, lblcol, remarkscol, stmtdtlcol) \
                VALUES ({id}, %s, %s, %s, %s, %s, %s)", matrixstr)
                conn.commit()
                count = cur.rowcount
                logger.debug(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
                if count <= 0 or dcount < 0: raise psycopg2.OperationalError(f"Fail to save mapping matrix (Mapping name={name}).")

            # At last perform rules deletion (if any)
            if del_iid not in (None, ''):
                args = "({0})".format(",".join(f"'{i}'" for i in del_iid))
                sql = f"DELETE FROM {Database.SCHEMA_FIN}.mappingrules WHERE gid = {id} AND col IN {args}"
                cur.execute(sql)
                conn.commit()
                dcount = cur.rowcount
                logger.debug(f"cur.query (rowcount)={cur.query} ({cur.rowcount})")
                if dcount <= 0: raise psycopg2.OperationalError(f"Fail to remove deleted mapping rules (Mapping name={name}).")
            else:
                dcount = 0
            cur.close()            
    except psycopg2.OperationalError as err:
        logger.error(err)
        conn.rollback()
        raise psycopg2.OperationalError(err)
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()        
    return {"id": id, "count": count, "dcount": dcount}

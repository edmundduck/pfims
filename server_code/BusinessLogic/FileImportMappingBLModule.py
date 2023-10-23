import anvil.server
from datetime import date, datetime
from ..CashMgtProcess import FileUploadMappingModule
from ..SysProcess import SystemModule as sysmod
from ..SysProcess import LoggingModule
from ..Utils import Helper

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.

logger = LoggingModule.ServerLogger()

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
    """

    userid = sysmod.get_current_userid()
    currenttime = datetime.now()

    # Prepare data for mappinggroup
    mgroup = (int(userid), id, name, filetype_id, currenttime) if id else (int(userid), name, filetype_id, currenttime)
    logger.trace('mgroup=', mgroup)
    
    tbl_def_dict = Helper.to_dict_of_list(FileUploadMappingModule.generate_expense_tbl_def_list())
    mrules = []
    matrixobj = {k: [] for k in tbl_def_dict.get('col_code')}
    for rule in rules:
        mrules.append([id, rule[0], rule[1], rule[2], rule[3] if rule[2] and rule[3] else None, rule[4]])
        matrixobj[rule[1]] = matrixobj[rule[1]] + [rule[0]] if matrixobj[rule[1]] else [rule[0]]
    logger.trace('mrules=', mrules)
    
    mmatrix = generate_mapping_matrix(matrixobj, tbl_def_dict.get('col_code'))
    logger.trace('mmatrix=', mmatrix)
    
    # mdelete = "({0})".format(",".join(f"'{i}'" for i in del_iid))
    mdelete = del_iid
    logger.trace('mdelete=', mdelete)

    return FileUploadMappingModule.save_mapping_group_rules(id, mgroup, mrules, mmatrix, mdelete)

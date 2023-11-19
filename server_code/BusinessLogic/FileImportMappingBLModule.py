import anvil.server
from datetime import date, datetime
from ..DataAccess import FileImportMappingDAModule
from ..ServerUtils.LoggingModule import ServerLogger
from ..Utils import Helper

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.

logger = ServerLogger()

@anvil.server.callable("init_cache_upload_mapping")
@logger.log_function
def init_cache_upload_mapping():
    from ..DataAccess import FileImportMappingDAModule
    exp_tbl_def_list = FileImportMappingDAModule.generate_expense_tbl_def_list()
    upload_action_list = FileImportMappingDAModule.generate_upload_action_list()
    return exp_tbl_def_list, upload_action_list
    
@logger.log_function
def generate_mapping_matrix(matrix, col_def):
    """
    Generate the whole mapping matrix to be used by Pandas columns combination based on mapping rules.

    Examples as follow,
    matrix= {'D': ['A', 'L'], 'AC': ['D'], 'AM': ['C', 'K'], 'L': ['E'], 'R': ['B'], 'SD': []}
    col_def= ['D', 'AC', 'AM', 'L', 'R', 'SD']
    result= [['J', '', 'C', 'H', '', 'B'], ['J', '', 'F', 'H', '', 'B']]

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

@anvil.server.callable("proc_save_mapping")
@logger.log_function
def proc_save_mapping(import_grp, del_iid=None):
    """
    Process data for updating import mapping data.

    Parameters:
        import_grp (ImportMappingGroup): The import mapping group object containing all group and rules detail.
        del_iid (string): The string of IID concatenated by comma to be deleted
        id (int): The ID of the mapping group.
        name (string): The mapping group name.
        filetype (list): The selected filetype ID.
        rules (list): The list of criteria of the rule to be saved.
        desc (string): The description of the mapping rule.

    Returns:
        id (int): The ID of the mapping group.
        count (int): The mapping matrix row count.
        result (list of dict): The merged data of both mapping rules and mapping groups grouped by mapping group ID.
    """
    from ..Error.AppError import AppError

    # Validation
    if not import_grp.is_valid():
        if isinstance(import_grp.is_valid(), AppError):
            raise import_grp.is_valid().get_error()
        else:
            raise TypeError('Backend validation error in import mapping data.')

    # Save mappinggroup
    id = FileImportMappingDAModule.save_mapping_group(import_grp)
    # Required or all mapping rules will have no updated group ID
    import_grp = import_grp.set_id(id)
    
    # Prepare data for mappingrules
    logger.trace('mrules=', [str(r) for r in import_grp.get_mapping_rules()])
    
    # Prepare data for mappingmatrix
    tbl_def_dict = Helper.to_dict_of_list(FileImportMappingDAModule.generate_expense_tbl_def_list())
    matrixobj = {k: [] for k in tbl_def_dict.get('col_code')}
    for rule in import_grp.get_mapping_rules():
        tbl_def_field_id = rule.get_mapped_column_type()
        column_id = rule.get_column_id()
        matrixobj[tbl_def_field_id] = matrixobj[tbl_def_field_id] + [column_id] if matrixobj[tbl_def_field_id] else [column_id]
    mmatrix = generate_mapping_matrix(matrixobj, tbl_def_dict.get('col_code'))
    logger.trace('mmatrix=', mmatrix)
    
    # Prepare deletion for mappingrules
    # mdelete = ','.join(i for i in del_iid) if del_iid else None
    # logger.trace('mdelete=', mdelete)

    # Save mappingrules, mappingmatrix and mappingrules deletion
    count = FileImportMappingDAModule.save_mapping_rules_n_matrix(import_grp, mmatrix, del_iid)

    # Return the saved mapping group and rules 
    result = FileImportMappingDAModule.select_mapping_rules(id)
    return id, count, result

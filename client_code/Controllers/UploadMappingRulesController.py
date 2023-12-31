import anvil.server
from ..Utils.Constants import CacheKey
from ..Utils.Logger import ClientLogger

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

logger = ClientLogger()

@logger.log_function
def init_cache():
    """
    Call one server function to preload all caches required by the form.
    """
    from ..Utils.ClientCache import ClientDropdownCache
    cache1 = ClientDropdownCache(CacheKey.DD_EXPENSE_TBL_DEF)
    cache2 = ClientDropdownCache(CacheKey.DD_IMPORT_EXTRA_ACTION)
    if any((
        cache1.is_empty(), cache1.is_expired(), cache2.is_empty(), cache2.is_expired()
    )):
        data_to_cache = anvil.server.call('init_cache_upload_mapping')
        cache1.set_cache(data_to_cache[0])
        cache2.set_cache(data_to_cache[1])

def generate_accounts_dropdown(reload=False):
    """
    Access accounts dropdown from either client cache or generate from DB data returned from server side.

    Parameters:
        reload (Boolean): Optional. True if clear cache is required. False by default.

    Returns:
        cache.get_cache (list): Accounts dropdown formed by accounts DB table data.
    """
    from . import AccountMaintController
    return AccountMaintController.generate_accounts_dropdown(reload)

def generate_labels_dropdown(reload=False):
    """
    Access labels dropdown from either client cache or generate from DB data returned from server side.

    Parameters:
        data (list of RealDictRow): Optional. The data list returned from the DB table to replace the client cache, should the client cache not already contain the data.
        reload (Boolean): Optional. True if clear cache is required. False by default.

    Returns:
        cache.get_cache (list): Labels dropdown formed by labels DB table data.
    """
    from . import LabelMaintController
    return LabelMaintController.generate_labels_dropdown(reload)

def generate_expense_table_definition_dropdown():
    """
    Access reference data - expense table definition dropdown from either client cache or generate from DB data returned from server side.

    Returns:
        cache.get_cache (list): Expense table definition dropdown formed by expense table definition DB table data.
    """
    from ..Utils.ClientCache import ClientDropdownCache
    cache = ClientDropdownCache(CacheKey.DD_EXPENSE_TBL_DEF)
    return cache.get_cache()

def generate_import_extra_action_dropdown():
    """
    Access reference data - import extra action dropdown from either client cache or generate from DB data returned from server side.

    Returns:
        cache.get_cache (list): Import extra action dropdown formed by import extra action DB table data.
    """
    from ..Utils.ClientCache import ClientDropdownCache
    cache = ClientDropdownCache(CacheKey.DD_IMPORT_EXTRA_ACTION)
    return cache.get_cache()

def generate_file_mapping_type_dropdown():
    """
    Access reference data - file mapping type dropdown from either client cache or generate from DB data returned from server side.

    Returns:
        cache.get_cache (list): File mapping type dropdown formed by import file type DB table data.
    """
    from . import ExpenseFileUploadController
    return ExpenseFileUploadController.generate_file_mapping_type_dropdown()

def get_account_dropdown_selected_item(acct_id):
    """
    Return a complete key based on a partial account ID which is a part of the key in a dropdown list.

    Parameters:
        acct_id (int): The account ID.

    Returns:
        selected_item (list): Complete key of the selected item in account dropdown.
    """
    from . import AccountMaintController
    return AccountMaintController.get_account_dropdown_selected_item(acct_id)

def get_label_dropdown_selected_item(lbl_id):
    """
    Return a complete key based on a partial label ID which is a part of the key in a dropdown list.

    Parameters:
        lbl_id (int): The label ID.

    Returns:
        selected_item (list): Complete key of the selected item in label dropdown.
    """
    from . import LabelMaintController
    return LabelMaintController.get_label_dropdown_selected_item(lbl_id)

def get_expense_table_definition_dropdown_selected_item(id):
    """
    Return a complete key based on a partial label ID which is a part of the key in a dropdown list.

    Parameters:
        id (int): The DB table column definition ID.

    Returns:
        selected_item (list): Complete key of the selected item in expense table definition dropdown.
    """
    from ..Utils.ClientCache import ClientDropdownCache
    cache = ClientDropdownCache(CacheKey.DD_EXPENSE_TBL_DEF)
    selected_item = cache.get_complete_key(id)
    return selected_item

def get_import_extra_action_dropdown_selected_item(id):
    """
    Return a complete key based on a partial label ID which is a part of the key in a dropdown list.

    Parameters:
        id (int): The import extra action ID.

    Returns:
        selected_item (list): Complete key of the selected item in import extra action dropdown.
    """
    from ..Utils.ClientCache import ClientDropdownCache
    cache = ClientDropdownCache(CacheKey.DD_IMPORT_EXTRA_ACTION)
    selected_item = cache.get_complete_key(id)
    return selected_item

def populate_repeating_panel_items(rp_items=None, reload=False, del_iid=None):
    """
    Populate repeating panel items with either mapping from server or blank record.

    Parameters:
        rp_items (list of dict): Repeating panel item.
        reload (boolean): Reload the whole repeating panel to filter unwanted rows if True.

    Returns:
        result (list of dict): A list of data padded with blank items for repeating panel.
    """
    def filter_valid_rows(row):
        if del_iid and row.get('id') == int(del_iid):
            # Filter out all rows in deleted IID cache
            return False
        if all(v is None for v in row.values()):
            # Filter out all None rows
            return False
        return True

    logger.trace(f"Param={rp_items} / {reload} / {del_iid}")
    if rp_items:
        result = list(filter(filter_valid_rows, rp_items)) if reload else [{} for i in range(1)] + rp_items
        logger.trace('rp_items with filter=', result)
    else:
        mappings = anvil.server.call('select_mapping_rules')
        result = mappings if mappings else [{} for i in range(1)]
        logger.trace('rp_items init load', result)
    return result

def add_mapping_rules_criteria(user_input):
    """
    Add criteria into mapping rule.

    Parameters:
        user_input (dict): Dictionary of all user selected dropdown values.

    Returns:
        result (list of dict): A list of data padded with blank items for repeating panel.
    """
    from ..Utils.Constants import FileImportExcelColumnMappingExtraAction, UploadMappingRulesInput
    action = user_input.get(UploadMappingRulesInput.ACTION)[0] if user_input and isinstance(user_input.get(UploadMappingRulesInput.ACTION), list) else user_input.get(UploadMappingRulesInput.ACTION)
    acct = user_input.get(UploadMappingRulesInput.ACCOUNT)[0] if user_input and isinstance(user_input.get(UploadMappingRulesInput.ACCOUNT), list) else user_input.get(UploadMappingRulesInput.ACCOUNT)
    lbl = user_input.get(UploadMappingRulesInput.LABEL)[0] if user_input and isinstance(user_input.get(UploadMappingRulesInput.LABEL), list) else user_input.get(UploadMappingRulesInput.LABEL)
    target_id = lbl if action == FileImportExcelColumnMappingExtraAction.LABEL else acct
    properties_list, rule = _generate_single_mapping_rule(
        user_input.get(UploadMappingRulesInput.EXCEL_COL),
        user_input.get(UploadMappingRulesInput.DATA_COL),
        user_input.get(UploadMappingRulesInput.ACTION),
        target_id
    )
    return properties_list, rule

@logger.log_function
def _generate_single_mapping_rule(excelcol, datacol_id, extraact_id, extratgt_id, **event_args):
    from ..Entities.ImportMappingRule import ImportMappingRule
    from ..Utils.Constants import FileImportExcelColumnMappingExtraAction, Icons
    logger.debug(f"excelcol={excelcol}, datacol_id={datacol_id}, extraact_id={extraact_id}, extratgt_id={extratgt_id}")
    datacol_id, datacol_name = datacol_id if datacol_id and isinstance(datacol_id, list) else get_expense_table_definition_dropdown_selected_item(datacol_id) if datacol_id else [None, None]
    action_id, action_name = extraact_id if extraact_id and isinstance(extraact_id, list) else get_import_extra_action_dropdown_selected_item(extraact_id) if extraact_id else [None, None]
    target_id, target_name = [None, None] if not extratgt_id else extratgt_id if extratgt_id and isinstance(extratgt_id, list) else (
        get_label_dropdown_selected_item(extratgt_id) if action_id == FileImportExcelColumnMappingExtraAction.LABEL else get_account_dropdown_selected_item(extratgt_id)
    )
    rule_desc = f"Map Excel column {excelcol} to data column {datacol_name}."
    rule_desc = f"{rule_desc} Extra action(s): {action_name} {target_name}" if action_name is not None else rule_desc
    rule_dict = {
        ImportMappingRule.field_column_id(): excelcol,
        ImportMappingRule.field_mapped_column_type(): datacol_id,
        ImportMappingRule.field_extra_action(): action_id,
        ImportMappingRule.field_extra_action_target_code(): target_id if action_id is not None else None,
        ImportMappingRule.field_rule_desc(): rule_desc
    }

    return rule_dict, rule_desc

@logger.log_function
def generate_all_mapping_rules(rules):
    result = []
    for r in rules:
        excelcol, datacol_id, extraact_id, extratgt_id = r
        # Without converting to int it cannot fetch the value in get method below
        extratgt_id = int(extratgt_id) if extratgt_id is not None else extratgt_id
        result.append(_generate_single_mapping_rule(excelcol, datacol_id, extraact_id, extratgt_id))
    return result

@logger.log_function
def save_mapping_criteria(id, name, filetype, rules, del_iid, desc):
    """
    Convert the fields from the form for saving the mapping rule change in backend.

    Parameters:
        id (int): The mapping rule ID to be saved.
        name (string): The mapping rule name.
        filetype (list): The selected filetype from dropdown.
        rules (list): The list of criteria of the rule to be saved.
        del_iid (string): The criteria item ID (iid) to be removed during the update.
        desc (string): The description of the mapping rule.
        
    Returns:
        result[0] (dict): Includes mapping group ID; successful insert/update row count (count), otherwise None; and successful delete row count (dcount), otherwise None.
    """
    from datetime import date, datetime
    from .. import Global
    from ..Entities.ImportMappingGroup import ImportMappingGroup
    if not id:
        id = None
    filetype_id, _ = filetype if filetype and isinstance(filetype, list) else [filetype, None]
    del_iid = del_iid[:-1].split(",") if del_iid else None
    currenttime = datetime.now()
    imp_grp = ImportMappingGroup()
    imp_grp = imp_grp.set_user_id(Global.userid).set_id(id).set_name(name).set_file_type(filetype_id).set_description(desc).set_lastsaved_time(currenttime).set_mapping_rules(rules)
    id, _, result = anvil.server.call('proc_save_mapping', imp_grp, del_iid)
    if not result:
        raise RuntimeError('Error occurs in proc_save_mapping.')
    return id

@logger.log_function
def delete_mapping_criteria(id):
    """
    Convert the fields from the form for deleting the mapping rule change in backend.

    Parameters:
        id (int): The mapping rule ID to be deleted.
        
    Returns:
        result (int): Successful delete row count, otherwise None.
    """
    result = anvil.server.call('delete_mapping', id)
    if not result:
        raise RuntimeError('Error occurs in delete_mapping.')
    return result

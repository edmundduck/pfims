import anvil.server
from ..Utils.Constants import CacheKey
from ..Utils.Logger import ClientLogger

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

logger = ClientLogger()

def generate_accounts_dropdown(data=None, reload=False):
    """
    Access accounts dropdown from either client cache or generate from DB data returned from server side.

    Parameters:
        data (list of RealRowDict): Optional. The data list returned from the DB table to replace the client cache, should the client cache not already contain the data.
        reload (Boolean): Optional. True if clear cache is required. False by default.

    Returns:
        cache.get_cache (list): Accounts dropdown formed by accounts DB table data.
    """
    from . import AccountMaintController
    return AccountMaintController.generate_accounts_dropdown(data, reload)

def generate_labels_dropdown(data=None, reload=False):
    """
    Access labels dropdown from either client cache or generate from DB data returned from server side.

    Parameters:
        data (list of RealRowDict): Optional. The data list returned from the DB table to replace the client cache, should the client cache not already contain the data.
        reload (Boolean): Optional. True if clear cache is required. False by default.

    Returns:
        cache.get_cache (list): Labels dropdown formed by labels DB table data.
    """
    from . import LabelMaintController
    return LabelMaintController.generate_labels_dropdown(data, reload)

def generate_expense_table_definition_dropdown():
    """
    Access reference data - expense table definition dropdown from either client cache or generate from DB data returned from server side.

    Returns:
        cache.get_cache (list): Expense table definition dropdown formed by expense table definition DB table data.
    """
    from ..Utils.ClientCache import ClientCache
    cache = ClientCache(CacheKey.DD_EXPENSE_TBL_DEF, None)
    if cache.is_empty():
        rows = anvil.server.call('generate_expense_tbl_def_dropdown')
        new_dropdown = list((r['col_name'], [r['col_code'], r['col_name']]) for r in rows)
        cache.set_cache(new_dropdown)
    return cache.get_cache()

def generate_import_extra_action_dropdown():
    """
    Access reference data - import extra action dropdown from either client cache or generate from DB data returned from server side.

    Returns:
        cache.get_cache (list): Import extra action dropdown formed by import extra action DB table data.
    """
    from ..Utils.ClientCache import ClientCache
    cache = ClientCache(CacheKey.DD_IMPORT_EXTRA_ACTION, None)
    if cache.is_empty():
        rows = anvil.server.call('generate_upload_action_dropdown')
        new_dropdown = list((r['action'], [r['id'], r['action']]) for r in rows)
        cache.set_cache(new_dropdown)
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
        if del_iid and row.get('id') == del_iid:
            # Filter out all rows in deleted IID cache
            return False
        if all(v is None for v in row.values()):
            # Filter out all None rows
            return False
        return True

    if rp_items:
        result = list(filter(filter_valid_rows, rp_items)) if reload else [{} for i in range(1)] + rp_items
        logger.trace('rp_items blank=', result)
    else:
        mappings = anvil.server.call('select_mapping_rules')
        result = mappings if mappings else [{} for i in range(1)]
        logger.trace('rp_items with data=', result)
    return result

def add_mapping_rules_criteria(user_input, is_new=False):
    """
    Add criteria into mapping rule.

    Parameters:
        user_input (dict): Dictionary of all user selected dropdown values.
        is_new (boolean): True if this criteria is newly created by user.

    Returns:
        result (list of dict): A list of data padded with blank items for repeating panel.
    """
    from ..Utils.Constants import FileImportExcelColumnMappingExtraAction, UploadMappingRulesInput
    excel = user_input.get(UploadMappingRulesInput.EXCEL_COL)
    data = user_input.get(UploadMappingRulesInput.DATA_COL)[0] if isinstance(user_input.get(UploadMappingRulesInput.DATA_COL), list) else user_input.get(UploadMappingRulesInput.DATA_COL)
    action = user_input.get(UploadMappingRulesInput.ACTION)[0] if isinstance(user_input.get(UploadMappingRulesInput.ACTION), list) else user_input.get(UploadMappingRulesInput.ACTION)
    acct = user_input.get(UploadMappingRulesInput.ACCOUNT)[0] if isinstance(user_input.get(UploadMappingRulesInput.ACCOUNT), list) else user_input.get(UploadMappingRulesInput.ACCOUNT)
    lbl = user_input.get(UploadMappingRulesInput.LABEL)[0] if isinstance(user_input.get(UploadMappingRulesInput.LABEL), list) else user_input.get(UploadMappingRulesInput.LABEL)
    target_id = lbl if action == FileImportExcelColumnMappingExtraAction.LABEL else acct
    _generate_mapping_rule(excel, data, action, target_id)
    return result

@logger.log_function
def _generate_mapping_rule(self, excelcol, datacol_id, extraact_id, extratgt_id, is_new=False, **event_args):
    from .....Utils.Constants import ColorSchemes, Icons
    logger.debug(f"excelcol={excelcol}, datacol_id={datacol_id}, extraact_id={extraact_id}, extratgt_id={extratgt_id}")
    dict_exp_tbl_def = {k[1][0]: k[1][1] for k in UploadMappingRulesController.generate_expense_table_definition_dropdown()}
    dict_extraact = {k[1][0]: k[1][1] for k in UploadMappingRulesController.generate_import_extra_action_dropdown()}
    dict_lbl = {k[1][0]: k[1][1] for k in UploadMappingRulesController.generate_labels_dropdown()}
    dict_acct =  {k[1][0]: k[1][1] for k in UploadMappingRulesController.generate_accounts_dropdown()}
    datacol = dict_exp_tbl_def.get(datacol_id, None)
    extraact = dict_extraact.get(extraact_id, None)
    extratgt = dict_lbl.get(extratgt_id, None) if extraact_id == "L" else dict_acct.get(extratgt_id, None)
    rule = f"{self.row_lbl_1.text}{excelcol}{self.row_lbl_2.text}{datacol}."
    rule = f"{rule} Extra action(s): {extraact} {extratgt}" if extraact is not None else rule
    
    lbl_obj = Label(text=rule, font_size=12, foreground='indigo', icon=Icons.BULLETPOINT)
    fp = FlowPanel(spacing_above="small", spacing_below="small", tag=[excelcol, datacol_id, extraact_id, extratgt_id, rule, is_new])
    b = Button(
        icon=Icons.REMOVE,
        foreground=ColorSchemes.BUTTON_BG,
        font_size=12,
        align="left",
        spacing_above="small",
        spacing_below="small",
    )
    self.add_component(fp)
    fp.add_component(lbl_obj)
    fp.add_component(b)
    b.set_event_handler('click', self.mapping_button_minus_click)

@logger.log_function
def _generate_all_mapping_rules(self, rules, **event):
    for r in rules:
        excelcol, datacol_id, extraact_id, extratgt_id = r
        # Without converting to int it cannot fetch the value in get method below
        extratgt_id = int(extratgt_id) if extratgt_id is not None else extratgt_id
        self._generate_mapping_rule(excelcol, datacol_id, extraact_id, extratgt_id)

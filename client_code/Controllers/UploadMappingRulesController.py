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
        
import anvil.server
from ..Utils.Constants import CacheKey, ExpenseConfig
from ..Utils.Logger import ClientLogger

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

logger = ClientLogger()

@logger.log_function
def generate_expense_tabs_dropdown(data=None, reload=False):
    """
    Access expense tabs dropdown from either client cache or generate from DB data returned from server side.

    Parameters:
        data (list of RealRowDict): Optional. The data list returned from the DB table to replace the client cache, should the client cache not already contain the data.
        reload (Boolean): Optional. True if clear cache is required. False by default.

    Returns:
        cache.get_cache (list): Expense tabs dropdown formed by expense tabs DB table data.
    """
    from ..Utils.ClientCache import ClientCache
    cache_data = list((r['tab_name'] + " (" + str(r['tab_id']) + ")", [r['tab_id'], r['tab_name']]) for r in data) if data else None
    cache = ClientCache(CacheKey.DD_EXPENSE_TAB, cache_data)
    if reload:
        cache.clear_cache()
    if cache.is_empty():
        rows = anvil.server.call('generate_expensetabs_dropdown')
        new_dropdown = list((r['tab_name'] + " (" + str(r['tab_id']) + ")", [r['tab_id'], r['tab_name']]) for r in rows)
        cache.set_cache(new_dropdown)
    return cache.get_cache()

@logger.log_function
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

@logger.log_function
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

def enable_expense_group_delete_button(group_selection):
    """
    Enable or disable the expense group delete button.

    Parameters:
        group_selection (list): The selected value in list from the expense group dropdown.
        
    Returns:
        Boolean: True for enable, false for disable.
    """
    group_id = group_selection[0] if isinstance(group_selection, (list, tuple)) else group_selection
    return False if group_id in (None, '') or str(group_id).isspace() else True

def populate_repeating_panel_items(rp_items=None):
    """
    Populate repeating panel items with data padded with a list of blank items.

    Number of blank items to pad is based on the number defined in Constants module.

    Parameters:
        rp_items (list of dict): Repeating panel item.

    Returns:
        result (list of dict): A list of data padded with blank items for repeating panel.
    """
    from ..Entities.ExpenseTransaction import ExpenseTransaction
    def filter_valid_rows(row):
        cache_del_iid = ClientCache(CacheKey.EXP_INPUT_DEL_IID, [])
        if row.get('iid', None) and row.get('iid') in cache_del_iid.get_cache():
            # Filter out all rows in deleted IID cache
            return False
        if all(v is None for v in row.values()):
            # Filter out all None rows
            return False
        return True

    if rp_items:
        diff = ExpenseConfig.DEFAULT_ROW_NUM - len(rp_items)
        result = list(filter(filter_valid_rows, rp_items)) + [ExpenseTransaction().copy().get_dict() for i in range(diff) if diff > 0]
    else:
        result = [ExpenseTransaction().copy().get_dict() for i in range(ExpenseConfig.DEFAULT_ROW_NUM)]
    return result
        
def replace_repeating_panel_iid(iid, rp_items):
    """
    Replace repeating panel items IID.

    Parameters:
        iid (int): New IID.
        rp_items (list of dict): Repeating panel item.

    Returns:
        LD (list of dict): Repeating panel item with replaced new IID.
    """
    DL = {k: [dic[k] for dic in rp_items] for k in rp_items[0]}
    DL['iid'] = iid
    LD = [dict(zip(DL, col)) for col in zip(*DL.values())]
    return LD

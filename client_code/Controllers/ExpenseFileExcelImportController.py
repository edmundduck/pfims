import anvil.server
from ..Utils.Constants import CacheKey
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
    from . import ExpenseInputController
    return ExpenseInputController.generate_expense_tabs_dropdown(data, reload)

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

@logger.log_function
def generate_labels_mapping_action_dropdown():
    """
    Access reference data - labels mappiong action dropdown from either client cache or generate from DB data returned from server side.

    Returns:
        cache.get_cache (list): Labels mappiong action dropdown formed by labels mappiong action DB table data.
    """
    from ..Utils.ClientCache import ClientCache
    cache = ClientCache(CacheKey.DD_LABEL_MAPPING_ACTION, None)
    if cache.is_empty():
        rows = anvil.server.call('generate_labels_mapping_action_list')
        new_dropdown = list((r['action'], [r['id'], r['action']]) for r in rows)
        cache.set_cache(new_dropdown)
    return cache.get_cache()

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

def get_labels_mapping_action_dropdown_selected_item(action):
    """
    Return a complete key based on a partial currency ID which is a part of the key in a dropdown list.

    Parameters:
        action (string): The labels mapping action ID.

    Returns:
        selected_item (list): Complete key of the selected item in labels mapping action dropdown.
    """
    from ..Utils.ClientCache import ClientCache
    cache = ClientCache(CacheKey.DD_LABEL_MAPPING_ACTION, None)
    if cache.is_empty():
        generate_labels_mapping_action_dropdown()
    selected_item = cache.get_complete_key(action)
    return selected_item

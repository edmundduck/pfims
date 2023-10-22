import anvil.server
from ..Utils.Constants import CacheKey, FileImportLabelExtraAction
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

def visible_account_label_map_to_dropdown(action_selection):
    """
    Make the account map to dropdown visible or invisible.

    Parameters:
        action_selection (list): Selected action from dropdown.

    Returns:
        result (boolean): True for visible, false for invisible.
    """
    action, _ = action_selection if action_selection is not None else [None, None]
    if action in (None, FileImportLabelExtraAction.SKIP):
        result = False
    elif action == FileImportLabelExtraAction.MAP:
        result = True
    elif action == FileImportLabelExtraAction.CREATE:
        result = False
    return result

def visible_account_label_textfield(action_selection):
    """
    Make the account text field visible or invisible.

    Parameters:
        action_selection (list): Selected action from dropdown.

    Returns:
        result (boolean): True for visible, false for invisible.
    """
    action, _ = action_selection if action_selection is not None else [None, None]
    if action in (None, FileImportLabelExtraAction.SKIP):
        result = False
    elif action == FileImportLabelExtraAction.MAP:
        result = False
    elif action == FileImportLabelExtraAction.CREATE:
        result = True
    return result

@logger.log_function
def populate_accounts_repeating_panel_items(data):
    """
    Populate accounts repeating panel items with data.

    Parameters:
        data (dataframe): Dataframe containing all transactions.

    Returns:
        result (list of dict): A list of data to populate to repeating panel.
    """
    DL_acct = {
        'srcacct': data,
        'action': [ None for i in range(len(data))] if data is not None else [ None ] ,
        'tgtacct': [ None for i in range(len(data))] if data is not None else [ None ] ,
        'newacct': data
    }
    logger.trace("DL_acct=", DL_acct)
    result = [dict(zip(DL_acct, col)) for col in zip(*DL_acct.values())]
    return result

@logger.log_function
def populate_labels_repeating_panel_items(data):
    """
    Populate labels repeating panel items with data.

    Parameters:
        data (dataframe): Dataframe containing all transactions.

    Returns:
        result (list of dict): A list of data to populate to repeating panel.
    """
    # Transpose Dict of Lists (DL) to List of Dicts (LD)
    # Ref - https://stackoverflow.com/questions/37489245/transposing-pivoting-a-dict-of-lists-in-python
    DL_lbl = {
        'srclbl': data,
        'action': [ None for i in range(len(data))] if data is not None else [ None ],
        # Prefill "labels map to" dropdown by finding high proximity choices
        'tgtlbl': anvil.server.call('predict_relevant_labels', data, generate_labels_dropdown()),
        'new': data
    }
    logger.trace("DL_lbl=", DL_lbl)
    result = [dict(zip(DL_lbl, col)) for col in zip(*DL_lbl.values())]
    return result

@logger.log_function
def update_excel_import_mapping(data, mapping_lbls, mapping_accts):
    """
    2nd process of Excel file import which is cropping the required statement detail part and then mapping accordingly.

    Parameters:
        data (dataframe): The dataframe to be updated with the mapping.
        mapping_lbls (list): The list of labels mapping from user's input.
        mapping_accts (list): The list of accounts mapping from user's input.

    Returns:
        df (dataframe): Processed dataframe.
    """
    logger.trace("mapping_lbls=", mapping_lbls)
    logger.trace("mapping_accts=", mapping_accts)
    df = anvil.server.call('proc_excel_update_mappings', data, mapping_lbls, mapping_accts)
    logger.trace("df=", df)
    return df
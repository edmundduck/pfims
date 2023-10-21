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

def populate_accounts_repeating_panel_items(data=None):
    """
    Populate accounts repeating panel items with data.

    Parameters:
        data (dataframe): Dataframe containing all transactions.

    Returns:
        result (list of dict): A list of data to populate to repeating panel.
    """
    DL_acct = {
        'srcacct': accounts,
        'action': [ None for i in range(len(accounts))] if accounts is not None else [ None ] ,
        'tgtacct': [ None for i in range(len(accounts))] if accounts is not None else [ None ] ,
        'newacct': accounts
    }
    logger.trace("DL_acct=", DL_acct)
    result = [dict(zip(DL_acct, col)) for col in zip(*DL_acct.values())]
    return result

def populate_labels_repeating_panel_items(data=None):
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
        'srclbl': labels,
        'action': [ None for i in range(len(labels))] if labels is not None else [ None ],
        # Prefill "labels map to" dropdown by finding high proximity choices
        'tgtlbl': predict_relevant_labels(labels, generate_labels_dropdown()),
        'new': labels
    }
    logger.trace("DL_lbl=", DL_lbl)
    result = [dict(zip(DL_lbl, col)) for col in zip(*DL_lbl.values())]
    return result

def predict_relevant_labels(srclbl, curlbl):
    """
    Return a label which has the highest proximity (a.k.a. the most matched) from the DB from the source label.

    Parameters:
        srclbl (list): The labels extracted from Excel to be compared.
        curlbl (list): The label dropdown from the DB labels table.

    Returns:
        score (list): Proximity score of each label, its order follows the order of the srclbl.
    """
    # Max 100, min 0
    min_proximity = 40
    score = []
    for s in srclbl:
        highscore = [0, None]
        for lbl in curlbl:
            similarity = fuzz.ratio(s, lbl[1][1])
            logger.trace(f"lbl={lbl[1][1]}, similarity={similarity}, highscore[0]={highscore[0]}")
            if similarity > highscore[0]:
                highscore = [similarity, [lbl[1][0], lbl[1][1]]]
        score.append(highscore[1] if highscore[0] > min_proximity else None)
    return score
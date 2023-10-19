import anvil.server
from ..Utils.Constants import CacheKey, ExpenseConfig
from ..Utils.Logger import ClientLogger

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

logger = ClientLogger()

@logger.log_function
def init_cache():
    """
    Call one server function to preload all caches required by the form.
    """
    from ..Utils.ClientCache import ClientCache
    data_to_cache = anvil.server.call('init_cache_stock_trading_txn_detail')
    cache = ClientCache(CacheKey.DD_EXPENSE_TAB, cache_data)
    cache = ClientCache(CacheKey.OBJ_EXPENSE_GRP, None)
    cache = ClientCache(CacheKey.EXP_INPUT_DEL_IID, [])
    cache = ClientCache(CacheKey.DD_ACCOUNT, cache_data)
    cache = ClientCache(CacheKey.DD_LABEL, cache_data)
    ClientCache(CacheKey.DD_BROKER, list((''.join([r['name'], ' [', r['ccy'], ']']), (r['broker_id'], r['name'], r['ccy'])) for r in data_to_cache[0]))
    ClientCache(CacheKey.DD_STOCK_JRN_GRP, list((''.join([r['template_name'], ' [', str(r['template_id']), ']']), (r['template_id'], r['template_name'])) for r in data_to_cache[1]))

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
        rows = anvil.server.call('generate_expense_groups_list')
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

def get_expense_tabs_dropdown_selected_item(exp_grp_id):
    """
    Return a complete key based on a partial currency ID which is a part of the key in a dropdown list.

    Parameters:
        exp_grp_id (int): The expense transaction group ID.

    Returns:
        selected_item (list): Complete key of the selected item in expense transaction group dropdown.
    """
    from ..Utils.ClientCache import ClientCache
    cache = ClientCache(CacheKey.DD_EXPENSE_TAB, None)
    if cache.is_empty():
        generate_expense_tabs_dropdown()
    selected_item = cache.get_complete_key(exp_grp_id)
    return selected_item

@logger.log_function
def __get_expense_transaction_group__(group_dropdown_selected, reload=False):
    """
    Return the expense transaction group object of the selected expense transaction group.

    Parameters:
        group_dropdown_selected (list): The selected value in list from the expense transaction group dropdown.
        reload (Boolean): Optional. True if clear cache is required. False by default.

    Returns:
        exp_grp (ExpenseTransactionGroup): An expense transaction group object.
    """
    from ..Entities.ExpenseTransactionGroup import ExpenseTransactionGroup
    from ..Utils.ClientCache import ClientCache
    exp_grp_id, _ = group_dropdown_selected if group_dropdown_selected else [None, None]
    cache = ClientCache(CacheKey.OBJ_EXPENSE_GRP, None)
    exp_grp = ExpenseTransactionGroup()
    if exp_grp_id:
        if not reload and not cache.is_empty() and cache.get_cache().get(exp_grp_id, None):
            exp_grp = cache.get_cache().get(exp_grp_id, None)
        else:
            exp_grp.set_id(exp_grp_id)
            exp_grp = anvil.server.call('proc_select_expense_group', exp_grp)
            cache.set_cache({exp_grp_id: exp_grp})
            logger.trace(f'exp_grp_id={exp_grp_id} / exp_grp={exp_grp} / transactions={list(str(j) for j in exp_grp.get_transactions()) if exp_grp.get_journals() else []}')
    return exp_grp

def get_group_name(group_dropdown_selected, reload=False):
    """
    Return the expense transaction group name of the selected expense transaction group.

    Parameters:
        group_dropdown_selected (list): The selected value in list from the expense transaction group dropdown.
        reload (Boolean): Optional. True if clear cache is required. False by default.

    Returns:
        exp_grp.get_name (string): Selected expense transaction group's name.
    """
    exp_grp = __get_expense_transaction_group__(group_dropdown_selected, reload)
    return exp_grp.get_name()

@logger.log_function
def get_transactions(group_dropdown_selected, reload=False):
    """
    Return all transactions under the selected expense transaction group.

    Parameters:
        group_dropdown_selected (list): The selected value in list from the expense transaction group dropdown.
        reload (Boolean): Optional. True if clear cache is required. False by default.

    Returns:
        exp_grp.get_transactions (list of dict): Selected expense transaction group's transactions in serialized form for frontend.
    """
    from ..Utils.ClientCache import ClientCache
    cache = ClientCache(CacheKey.EXP_INPUT_DEL_IID, [])
    exp_grp = __get_expense_transaction_group__(group_dropdown_selected, reload)
    cache.clear_cache()
    return list(j.get_dict() for j in exp_grp.get_transactions()) if exp_grp.get_transactions() else []

def get_blank_row_button_text(button_text):
    """
    Return the add blank row button text based on the constant defined.

    Parameters:
        button_text (string): The button text displayed.

    Returns:
        result (string): Updated text with the number of blank rows to add.
    """
    result = button_text.replace('%n', str(ExpenseConfig.DEFAULT_ROW_NUM))
    return result

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

def populate_repeating_panel_items(rp_items=None, reload=False):
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
        cache = ClientCache(CacheKey.EXP_INPUT_DEL_IID, [])
        if row.get('iid', None) and row.get('iid') in cache.get_cache():
            # Filter out all rows in deleted IID cache
            return False
        if all(v is None for v in row.values()):
            # Filter out all None rows
            return False
        return True

    if rp_items:
        diff = ExpenseConfig.DEFAULT_ROW_NUM - len(rp_items)
        result = list(filter(filter_valid_rows, rp_items)) + [ExpenseTransaction().copy().get_dict() for i in range(diff) if diff > 0] if reload else \
                [ExpenseTransaction().copy().get_dict() for i in range(diff) if diff > 0]
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

@logger.log_function
def save_expense_transaction_group(group_dropdown_selected, group_name, transactions):
    """
    Convert the fields from the form for saving the expense transaction group change in backend.

    Parameters:
        group_dropdown_selected (list): The selected value in list from the expense transaction group dropdown.
        group_name (string): The name of the selected expense transaction group.
        transactions (list of dict): A list of transactions from repeating panel to be inserted or updated.
        
    Returns:
        exp_grp (ExpenseTransactionGroup): An expense transaction group object.
    """
    from datetime import date, datetime
    from .. import Global
    from ..Entities.ExpenseTransactionGroup import ExpenseTransactionGroup
    from ..Utils.ClientCache import ClientCache
    cache = ClientCache(CacheKey.EXP_INPUT_DEL_IID, [])

    exp_grp_id_ori, exp_grp_name_ori = group_dropdown_selected if group_dropdown_selected is not None else [None, None]

    currenttime = datetime.now()
    exp_grp = ExpenseTransactionGroup()
    exp_grp = exp_grp.set_user_id(Global.userid).set_id(exp_grp_id_ori).set_name(group_name).set_transactions(transactions)\
        .set_submitted_status(False).set_created_time(currenttime).set_lastsaved_time(currenttime)
    # Has to assign to a variable otherwise value in cache will be updated by reference
    del_iid = cache.get_cache()
    exp_grp, result_update, result_delete = anvil.server.call('proc_save_exp_tab', exp_grp, del_iid)
    if not exp_grp:
        raise RuntimeError('Error occurs in proc_save_exp_grp expense transaction group creation or update phase.')
    elif result_update is None or result_delete is None:
        # result_update and result_delete can be 0, but cannot be None.
        raise RuntimeError('Error occurs in proc_save_exp_grp transaction deletion or update phase.')
    else:
        logger.trace('exp_grp=', exp_grp)
        cache.clear_cache()
    return exp_grp

@logger.log_function
def submit_expense_transaction_group(group_dropdown_selected, submitted=True):
    """
    Convert the fields from the form for submitting the expense transaction group change in backend.

    Parameters:
        group_dropdown_selected (list): The selected value in list from the expense transaction group dropdown.
        submitted (boolean): The submitte status of the selected expense transaction group.
        
    Returns:
        exp_grp (ExpenseTransactionGroup): A expense transaction group object.
    """
    from datetime import date, datetime
    from ..Entities.ExpenseTransactionGroup import ExpenseTransactionGroup
    from ..Utils.ClientCache import ClientCache
    cache = ClientCache(CacheKey.EXP_INPUT_DEL_IID, [])

    exp_grp_id, exp_grp_name = group_dropdown_selected if group_dropdown_selected is not None else [None, None]
    currenttime = datetime.now()
    exp_grp = ExpenseTransactionGroup()
    exp_grp = exp_grp.set_id(exp_grp_id).set_name(exp_grp_name).set_submitted_status(submitted).set_submitted_time(currenttime)
    result = anvil.server.call('submit_expense_group', exp_grp) if exp_grp_id else None
    if not result:
        raise RuntimeError('Error occurs in submit_expense_group.')
    else:
        logger.trace('result=', result)
        cache.clear_cache()
    return result

@logger.log_function
def delete_expense_transaction_group(group_dropdown_selected):
    """
    Convert the fields from the form for deleting the expense transaction group change in backend.

    Parameters:
        group_dropdown_selected (list): The selected value in list from the expense transaction group dropdown.
        
    Returns:
        result (int): Successful delete row count, otherwise None.
    """
    from ..Entities.ExpenseTransactionGroup import ExpenseTransactionGroup
    from ..Utils.ClientCache import ClientCache
    cache = ClientCache(CacheKey.EXP_INPUT_DEL_IID, [])

    exp_grp_id, exp_grp_name = group_dropdown_selected if group_dropdown_selected is not None else [None, None]
    exp_grp = ExpenseTransactionGroup()
    exp_grp = exp_grp.set_id(exp_grp_id).set_name(exp_grp_name)
    result = anvil.server.call('delete_expense_group', exp_grp) if exp_grp_id else None
    if not result:
        raise RuntimeError('Error occurs in delete_expense_group.')
    else:
        logger.trace('result=', result)
        cache.clear_cache()
    return result

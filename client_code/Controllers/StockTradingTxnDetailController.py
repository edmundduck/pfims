import anvil.server
import anvil.users
from ..Utils.Constants import CacheKey, LoggingLevel
from ..Utils.Logger import ClientLogger

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

logger = ClientLogger()

def init_cache():
    """
    Call one server function to preload all caches required by the form.
    """
    from ..Utils.ClientCache import ClientCache
    data_to_cache = anvil.server.call('init_cache_stock_trading_txn_detail')
    ClientCache(CacheKey.DD_BROKER, list((''.join([r['name'], ' [', r['ccy'], ']']), (r['broker_id'], r['name'], r['ccy'])) for r in data_to_cache[0]))
    ClientCache(CacheKey.DD_STOCK_JRN_GRP, list((''.join([r['template_name'], ' [', str(r['template_id']), ']']), (r['template_id'], r['template_name'])) for r in data_to_cache[1]))

def generate_brokers_dropdown(data=None, reload=False):
    """
    Access brokers dropdown from either client cache or generate from DB data returned from server side.

    Parameters:
        data (list of RealRowDict): Optional. The data list returned from the DB table to replace the client cache, should the client cache not already contain the data.
        reload (Boolean): Optional. True if clear cache is required. False by default.

    Returns:
        cache.get_cache (list): Brokers dropdown formed by partial brokers DB table data.
    """
    from . import UserSettingController
    return UserSettingController.generate_brokers_dropdown(data, reload)

@logger.log_function
def generate_stock_journal_groups_dropdown(data=None, reload=False):
    """
    Access stock journal groups dropdown from either client cache or generate from DB data returned from server side.

    Parameters:
        data (list of RealRowDict): Optional. The data list returned from the DB table to replace the client cache, should the client cache not already contain the data.
        reload (Boolean): Optional. True if clear cache is required. False by default.

    Returns:
        cache.get_cache (list): Currency dropdown formed by currency DB table data.
    """
    from ..Utils.ClientCache import ClientCache
    cache_data = list((''.join([r['template_name'], ' [', str(r['template_id']), ']']), (r['template_id'], r['template_name'])) for r in data) if data else None
    cache = ClientCache(CacheKey.DD_STOCK_JRN_GRP, cache_data)
    if reload:
        cache.clear_cache()
    if cache.is_empty():
        rows = anvil.server.call('generate_drafting_stock_journal_groups_list')
        new_dropdown = list((''.join([r['template_name'], ' [', str(r['template_id']), ']']), (r['template_id'], r['template_name'])) for r in rows)
        cache.set_cache(new_dropdown)
    return cache.get_cache()

@logger.log_function
def __get_stock_journal_group__(group_dropdown_selected, reload=False):
    """
    Return the stock journal group object of the selected stock journal group.

    Parameters:
        group_dropdown_selected (list): The selected value in list from the broker dropdown.
        reload (Boolean): Optional. True if clear cache is required. False by default.

    Returns:
        jrn_grp (StockJournalGroup): A stock journal group object.
    """
    from ..Utils.ClientCache import ClientCache
    jrn_grp_id, _ = group_dropdown_selected if group_dropdown_selected else [None, None]
    cache = ClientCache(CacheKey.OBJ_STOCK_JRN_GRP, None)
    if jrn_grp_id:
        if not reload and not cache.is_empty() and cache.get_cache().get(jrn_grp_id, None):
            jrn_grp = cache.get_cache().get(jrn_grp_id, None)
        else:
            jrn_grp = anvil.server.call('select_stock_journal_group', jrn_grp_id)
            jrn_list = anvil.server.call('select_stock_journals', jrn_grp_id)
            jrn_grp = jrn_grp.set_journals(jrn_list)
            cache.set_cache({jrn_grp_id: jrn_grp})
            logger.trace(f'jrn_grp_id={jrn_grp_id} / jrn_grp={jrn_grp} / journals={list(str(j) for j in jrn_grp.get_journals()) if jrn_grp.get_journals() else []}')
    else:
        from . import UserSettingController
        from ..Entities.StockJournalGroup import StockJournalGroup
        blank_jrn_grp = StockJournalGroup()
        jrn_grp = blank_jrn_grp.set_broker(UserSettingController.get_user_settings().get_broker())
        logger.trace(f'jrn_grp_id={jrn_grp_id} / blank_jrn_grp={blank_jrn_grp}')
    return jrn_grp

def get_group_name(group_dropdown_selected, reload=False):
    """
    Return the stock journal group name of the selected stock journal group.

    Parameters:
        group_dropdown_selected (list): The selected value in list from the broker dropdown.
        reload (Boolean): Optional. True if clear cache is required. False by default.

    Returns:
        jrn_grp.get_name (string): Selected stock journal group's name.
    """
    jrn_grp = __get_stock_journal_group__(group_dropdown_selected, reload)
    return jrn_grp.get_name()

@logger.log_function
def get_journals(group_dropdown_selected, reload=False):
    """
    Return all journals under the selected stock journal group.

    Parameters:
        group_dropdown_selected (list): The selected value in list from the broker dropdown.
        reload (Boolean): Optional. True if clear cache is required. False by default.

    Returns:
        jrn_grp.get_serialized_journals (string): Selected stock journal group's journals in serialized form for frontend.
    """
    jrn_grp = __get_stock_journal_group__(group_dropdown_selected, reload)
    return list(j.get_dict() for j in jrn_grp.get_journals()) if jrn_grp.get_journals() else []

def get_stock_journal_group_dropdown_selected_item(group_id):
    """
    Return a complete key based on a partial stock journal group ID which is a part of the key in a dropdown list.

    Parameters:
        group_id (int): The stock journal group ID.

    Returns:
        selected_item (list): Complete key of the selected item in stock journal group dropdown.
    """
    from ..Utils.ClientCache import ClientCache
    cache = ClientCache(CacheKey.DD_STOCK_JRN_GRP, None)
    if cache.is_empty():
        generate_stock_journal_groups_dropdown()
    selected_item = cache.get_complete_key(group_id)
    return selected_item

def get_broker_dropdown_selected_item(group_dropdown_selected=None):
    """
    Return a complete key based on a partial broker ID which is a part of the key in a dropdown list.

    Parameters:
        group_dropdown_selected (list): Optional. The selected value in list from the broker dropdown, otherwise the default broker will be loaded from user setting.

    Returns:
        selected_item (list): Complete key of the selected item in broker dropdown.
    """
    from ..Utils.ClientCache import ClientCache
    from . import UserSettingController
    cache = ClientCache(CacheKey.DD_BROKER, None)
    if group_dropdown_selected:
        jrn_grp = __get_stock_journal_group__(group_dropdown_selected)
        if cache.is_empty():
            UserSettingController.generate_brokers_dropdown()
        selected_item = cache.get_complete_key(jrn_grp.get_broker())
    else:
        selected_item = cache.get_complete_key(UserSettingController.get_user_settings().get_broker())
    return selected_item

def enable_stock_journal_group_submit_button(group_dropdown_selected):
    """
    Enable or disable the stock journal group submit button.

    Parameters:
        group_dropdown_selected (list): The selected value in list from the stock journal group dropdown.

    Returns:
        Boolean: True for enable, false for disable.
    """
    jrn_grp_id = group_dropdown_selected[0] if isinstance(group_dropdown_selected, (list, tuple)) else group_dropdown_selected
    return False if str(jrn_grp_id) in (None, '') or str(jrn_grp_id).isspace() else True

def enable_stock_journal_group_delete_button(group_dropdown_selected):
    """
    Enable or disable the stock journal group delete button.

    Parameters:
        group_dropdown_selected (list): The selected value in list from the stock journal group dropdown.

    Returns:
        Boolean: True for enable, false for disable.
    """
    jrn_grp_id = group_dropdown_selected[0] if isinstance(group_dropdown_selected, (list, tuple)) else group_dropdown_selected
    return False if str(jrn_grp_id) in (None, '') or str(jrn_grp_id).isspace() else True

@logger.log_function
def save_stock_journal_group(group_dropdown_selected, jrn_grp_name, broker_dropdown_selected, journals):
    """
    Convert the fields from the form for saving the stock journal group change in backend.

    Parameters:
        group_dropdown_selected (list): The selected value in list from the stock journal group dropdown.
        jrn_grp_name (string): The name of the selected stock journal group.
        broker_dropdown_selected (list): The selected value in list from the broker dropdown.
        journals (list): A list of journals from repeating panel to be inserted or updated.
        
    Returns:
        jrn_grp (StockJournalGroup): A stock journal group object.
    """
    from datetime import date, datetime
    from ..Entities.StockJournalGroup import StockJournalGroup
    from ..Utils.ClientCache import ClientCache
    cache = ClientCache(CacheKey.STOCK_INPUT_DEL_IID, None)

    jrn_grp_id_ori, jrn_grp_name_ori = group_dropdown_selected if group_dropdown_selected is not None else [None, None]
    broker_id, _, _ = broker_dropdown_selected if broker_dropdown_selected is not None else [None, None, None]

    currenttime = datetime.now()
    jrn_grp = StockJournalGroup()
    jrn_grp = jrn_grp.set_id(jrn_grp_id_ori).set_name(jrn_grp_name).set_broker(broker_id).set_journals(journals).set_submitted_status(False).set_created_time(currenttime).set_lastsaved_time(currenttime)
    # Has to assign to a variable otherwise value in cache will be updated by reference
    del_iid = cache.get_cache()
    jrn_grp, result_update, result_delete = anvil.server.call('proc_save_group_and_journals', jrn_grp, del_iid)
    if not jrn_grp:
        raise RuntimeError(f"Error occurs in proc_save_group_and_journals journal group creation or update phase.")
    elif result_update is None or result_delete is None:
        # result_update and result_delete can be 0, but cannot be None.
        raise RuntimeError(f"Error occurs in proc_save_group_and_journals journal deletion or update phase.")
    else:
        logger.trace('jrn_grp=', jrn_grp)
        cache.clear_cache()
    return jrn_grp

@logger.log_function
def submit_stock_journal_group(group_dropdown_selected):
    """
    Convert the fields from the form for submitting the stock journal group change in backend.

    Parameters:
        group_dropdown_selected (list): The selected value in list from the stock journal group dropdown.
        
    Returns:
        jrn_grp (StockJournalGroup): A stock journal group object.
    """
    from datetime import date, datetime
    from ..Entities.StockJournalGroup import StockJournalGroup
    from ..Utils.ClientCache import ClientCache
    cache = ClientCache(CacheKey.STOCK_INPUT_DEL_IID, None)

    jrn_grp_id, jrn_grp_name = group_dropdown_selected if group_dropdown_selected is not None else [None, None]
    currenttime = datetime.now()
    jrn_grp = StockJournalGroup()
    jrn_grp = jrn_grp.set_id(jrn_grp_id).set_name(jrn_grp_name).set_submitted_status(True).set_submitted_time(currenttime)
    result = anvil.server.call('submit_stock_journal_group', jrn_grp) if jrn_grp_id else None
    if not result:
        raise RuntimeError(f"Error occurs in submit_stock_journal_group.")
    else:
        logger.trace('result=', result)
        cache.clear_cache()
    return result

@logger.log_function
def delete_stock_journal_group(group_dropdown_selected):
    """
    Convert the fields from the form for deleting the stock journal group change in backend.

    Parameters:
        group_dropdown_selected (list): The selected value in list from the stock journal group dropdown.
        
    Returns:
        result (int): Successful delete row count, otherwise None.
    """
    from ..Entities.StockJournalGroup import StockJournalGroup
    from ..Utils.ClientCache import ClientCache
    cache = ClientCache(CacheKey.STOCK_INPUT_DEL_IID, None)

    jrn_grp_id, jrn_grp_name = group_dropdown_selected if group_dropdown_selected is not None else [None, None]
    jrn_grp = StockJournalGroup()
    jrn_grp = jrn_grp.set_id(jrn_grp_id).set_name(jrn_grp_name)
    result = anvil.server.call('delete_stock_journal_group', jrn_grp) if jrn_grp_id else None
    if not result:
        raise RuntimeError(f"Error occurs in delete_stock_journal_group.")
    else:
        logger.trace('result=', result)
        cache.clear_cache()
    return result

@logger.log_function
def calculate_amount(sell_amt, buy_amt, fee, qty):
    """
    Calculate all amount fields including stock profit and stock unit price during sell or buy.
    
    Parameters:
        sell_amt (float): Lump sum of the stock sold.
        buy_amt (float): Lump sum of the stock purchased.
        fee (float): Fee incurred after stock purchased and sold.
        qty (float): Stock quantity.

    Returns:
        sell_price (float): Stock unit sold price.
        buy_price (float): Stock unit bought price.
        profit (float): Stock profit.
    """
    sell_price = round(float(sell_amt) / float(qty), 2)
    buy_price = round(float(buy_amt) / float(qty), 2)
    profit = round(float(sell_amt) - float(buy_amt) - float(fee), 2)
    return [sell_price, buy_price, profit]

def delete_item(iid):
    """
    Add IID of a deleted item to client cache for later processing.

    Parameters:
        iid (int): The item ID (IID) of the deleted item.
    """
    from ..Utils.ClientCache import ClientCache
    cache = ClientCache(CacheKey.STOCK_INPUT_DEL_IID, None)

    if iid is not None:
        if cache.is_empty():
            cache.set_cache([iid])
        else:
            cache.get_cache().append(iid)
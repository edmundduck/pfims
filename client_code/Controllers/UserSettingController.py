import anvil.server
import anvil.users
from ..Entities.Setting import Setting
from ..Utils.Constants import CacheKey

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

def get_user_settings(data=None, reload=False):
    """
    Return user settings of the current logged on user.

    Returns:
        cache.get_cache (list): User's settings.
    """
    from ..Utils.ClientCache import ClientCache
    cache = ClientCache(CacheKey.USER_SETTINGS, data.get_dict())
    if reload: 
        cache.clear_cache()
    if cache.is_empty():
        rows = anvil.server.call('select_settings')
        cache.set_cache(rows.get_dict())
    return cache.get_cache()
    
def generate_brokers_dropdown(data=None, reload=False):
    """
    Access brokers dropdown from either client cache or generate from DB data returned from server side.

    Parameters:
        data (list of RealRowDict): The data list returned from the DB table to replace the client cache, should the client cache not already contain the data.
        reload (Boolean): True if clear cache is required. False by default.

    Returns:
        cache.get_cache (list): Brokers dropdown formed by partial brokers DB table data.
    """
    from ..Utils.ClientCache import ClientCache
    cache = ClientCache(CacheKey.BROKER, list((''.join([r['name'], ' [', r['ccy'], ']']), (r['broker_id'], r['name'], r['ccy'])) for r in data))
    if reload: 
        cache.clear_cache()
    if cache.is_empty():
        rows = anvil.server.call('generate_brokers_simplified_list')
        new_dropdown = list((''.join([r['name'], ' [', r['ccy'], ']']), (r['broker_id'], r['name'], r['ccy'])) for r in rows)
        cache.set_cache(new_dropdown)
    return cache.get_cache()

def generate_search_interval_dropdown(data=None):
    """
    Access search interval dropdown from either client cache or generate from DB data returned from server side.

    Parameters:
        data (list of RealRowDict): The data list returned from the DB table to replace the client cache, should the client cache not already contain the data.

    Returns:
        cache.get_cache (list): Search interval dropdown formed by search interval DB table data.
    """
    from ..Utils.ClientCache import ClientCache
    cache = ClientCache(CacheKey.SEARCH_INTERVAL, list((r['name'], r['id']) for r in data))
    if cache.is_empty():
        rows = anvil.server.call('generate_search_interval_list')
        new_dropdown = list((r['name'], r['id']) for r in rows)
        cache.set_cache(new_dropdown)
    return cache.get_cache()

def generate_currency_dropdown(data=None):
    """
    Access currency dropdown from either client cache or generate from DB data returned from server side.

    Parameters:
        data (list of RealRowDict): The data list returned from the DB table to replace the client cache, should the client cache not already contain the data.

    Returns:
        cache.get_cache (list): Currency dropdown formed by currency DB table data.
    """
    from ..Utils.ClientCache import ClientCache
    cache = ClientCache(CacheKey.CURRENCY, list((r['abbv'] + " " + r['name'] + " (" + r['symbol'] + ")" if r['symbol'] else r['abbv'] + " " + r['name'], r['abbv']) for r in data))
    if cache.is_empty():
        rows = anvil.server.call('generate_currency_list')
        new_dropdown = list((r['abbv'] + " " + r['name'] + " (" + r['symbol'] + ")" if r['symbol'] else r['abbv'] + " " + r['name'], r['abbv']) for r in rows)
        cache.set_cache(new_dropdown)
    return cache.get_cache()

def generate_submitted_journal_groups_dropdown(data=None, reload=False):
    """
    Access submitted stock journal groups dropdown from either client cache or generate from DB data returned from server side.

    Parameters:
        data (list of RealRowDict): The data list returned from the DB table to replace the client cache, should the client cache not already contain the data.
        reload (Boolean): True if clear cache is required. False by default.

    Returns:
        cache.get_cache (list): Submitted stock journal groups dropdown formed by stock journal groups DB table data.
    """
    from ..Utils.ClientCache import ClientCache
    cache = ClientCache(CacheKey.SUBMITTED_JRN_GRP, list((''.join([r['template_name'], ' [', str(r['template_id']), ']']), (r['template_id'], r['template_name'])) for r in data))
    if cache.is_empty():
        rows = anvil.server.call('generate_submitted_journal_groups_list')
        new_dropdown = list((''.join([r['template_name'], ' [', str(r['template_id']), ']']), (r['template_id'], r['template_name'])) for r in rows)
        cache.set_cache(new_dropdown)
    return cache.get_cache()

def get_broker_dropdown_selected_item(broker_id):
    """
    Return a complete key based on a partial broker ID which is a part of the key in a dropdown list.

    Returns:
        selected_item (list): Complete key of the selected item in broker dropdown.
    """
    from ..Utils.ClientCache import ClientCache
    brokers_dropdown = ClientCache(CacheKey.BROKER, None)
    if brokers_dropdown.is_empty():
        generate_brokers_dropdown()
    selected_item = brokers_dropdown.get_complete_key(broker_id)
    return selected_item

def enable_search_time_datefield(interval_selection):
    """
    Enable or disable the "search time" (from, to) date field.

    Returns:
        Boolean, Boolean: True for enable, false for disable.
    """
    from ..Utils.Constants import SearchInterval
    interval = interval_selection[0] if isinstance(interval_selection, (list, tuple)) else interval_selection
    return [True]*2 if interval == SearchInterval.INTERVAL_SELF_DEFINED else [False]*2

def set_search_time_datefield_value(interval_selection, date_from_value, date_to_value):
    """
    Set the "search time" (from, to) date field value.

    Returns:
        String, String: Return original values provided in parameters if it's user defined, otherwise None.
    """
    from ..Utils.Constants import SearchInterval
    interval = interval_selection[0] if isinstance(interval_selection, (list, tuple)) else interval_selection
    return [date_from_value, date_to_value] if interval == SearchInterval.INTERVAL_SELF_DEFINED else [None] *2

def enable_broker_action_button(broker_selection, broker_name):
    """
    Enable or disable the broker action buttons (Create, Update, Delete).

    Returns:
        Boolean, Boolean: True for enable, false for disable.
    """
    broker_id = broker_selection[0] if isinstance(broker_selection, (list, tuple)) else broker_selection
    return [False]*3 if (broker_id or broker_name) in (None, '') or broker_id.isspace() or broker_name.isspace() else [True]*3

def set_selected_broker_fields(broker_selection):
    """
    Set the broker name and currency based on broker dropdown.

    Returns:
        broker_id (String): Selected broker ID.
        broker_name (String): Selected broker name, None instead if broker ID is none or empty.
        broker_ccy (String): Selected broker currency, None instead if broker ID is none or empty.
    """
    if isinstance(broker_selection, (list, tuple)):
        broker_id, broker_name, broker_ccy = broker_selection
        if broker_id in (None, '') or broker_id.isspace():
            broker_name, broker_ccy = [None] *2
    else:
        broker_name, broker_ccy = [None] *2
    return [broker_id, broker_name, broker_ccy]

def visible_logging_panel():
    """
    Make the logging panel visible or invisible.

    Returns:
        Boolean: True for visible, false for invisible.
    """
    return True if anvil.app.environment.name in 'Dev' else False

def change_settings(broker_dropdown_selected, interval_dropdown_selected, datefrom, dateto, logging_level):
    """
    Convert the fields from the form for submitting the user settings change in backend.

    Parameters:
        broker_dropdown_selected (list): The selected value in list from the broker dropdown.
        interval_dropdown_selected (list): The selected value in list from the search interval.
        datefrom (date): The date to default search from.
        dateto (date): The date to default search to.
        logging_level (int): The user's logging level mostly based on Python's logging module, data type in DB is smallint.
        
    Returns:
        count (int): Successful update row count, otherwise None
    """
    from ..Utils.ClientCache import ClientCache
    from ..Utils.Constants import SearchInterval
    cache = ClientCache(CacheKey.USER_SETTINGS, None)
    broker_id, _, _ = broker_dropdown_selected if isinstance(broker_dropdown_selected, (list, tuple)) else [broker_dropdown_selected, None, None]
    print("BROKER_ID=", broker_id)
    search_interval = interval_dropdown_selected[0] if isinstance(interval_dropdown_selected, (list, tuple)) else interval_dropdown_selected
    if search_interval != SearchInterval.INTERVAL_SELF_DEFINED:
        datefrom, dateto = [None, None]
    count = anvil.server.call('proc_upsert_settings', Setting([None, broker_id, search_interval, datefrom, dateto, logging_level]))
    if not count:
        raise RuntimeError(f"Error occurs in proc_upsert_setting.")
    else:
        cache.clear_cache()
    return count


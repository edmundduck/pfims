import anvil.server
import anvil.users
from ..Entities.Setting import Setting
from ..Utils.Constants import CacheKey, LoggingLevel
from ..Utils.Logger import ClientLogger

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

logger = ClientLogger()

@logger.log_function
def initialize_data():
    """
    Get all the data for form initialization.

    Returns:
        list: A list of all functions return required by the form initialization.
    """
    from ..Utils.ClientCache import ClientDropdownCache
    cache1 = ClientDropdownCache(CacheKey.DD_BROKER)
    cache2 = ClientDropdownCache(CacheKey.DD_SEARCH_INTERVAL)
    cache3 = ClientDropdownCache(CacheKey.DD_CURRENCY)
    cache4 = ClientDropdownCache(CacheKey.DD_SUBMITTED_JRN_GRP)
    if any((
        cache1.is_empty(), cache1.is_expired(), cache2.is_empty(), cache2.is_expired(),
        cache3.is_empty(), cache3.is_expired(), cache4.is_empty(), cache4.is_expired()
    )):
        brokers, search_interval, ccy, submitted_group_list = anvil.server.call('proc_init_settings')
        cache1.set_cache(brokers)
        cache2.set_cache(search_interval)
        cache3.set_cache(ccy)
        cache4.set_cache(submitted_group_list)

def get_user_settings():
    """
    Get latest user settings of the current logged on user and load to Global as user setting cache.
    """
    from .. import Global
    setting = anvil.server.call('select_settings')
    Global.settings = setting

@logger.log_function
def generate_brokers_dropdown(reload=False):
    """
    Access brokers dropdown from either client cache or generate from DB data returned from server side.

    Parameters:
        reload (Boolean): Optional. True if clear cache is required. False by default.

    Returns:
        cache.get_cache (list): Brokers dropdown formed by partial brokers DB table data.
    """
    from ..Utils.ClientCache import ClientDropdownCache
    cache = ClientDropdownCache(CacheKey.DD_BROKER)
    if reload:
        cache.clear_cache()
    return cache.get_cache()

@logger.log_function
def generate_search_interval_dropdown():
    """
    Access search interval dropdown from either client cache or generate from DB data returned from server side.

    Returns:
        cache.get_cache (list): Search interval dropdown formed by search interval DB table data.
    """
    from ..Utils.ClientCache import ClientDropdownCache
    cache = ClientDropdownCache(CacheKey.DD_SEARCH_INTERVAL)
    return cache.get_cache()

@logger.log_function
def generate_currency_dropdown():
    """
    Access currency dropdown from either client cache or generate from DB data returned from server side.

    Returns:
        cache.get_cache (list): Currency dropdown formed by currency DB table data.
    """
    from ..Utils.ClientCache import ClientDropdownCache
    cache = ClientDropdownCache(CacheKey.DD_CURRENCY)
    return cache.get_cache()

@logger.log_function
def generate_submitted_journal_groups_dropdown(reload=False):
    """
    Access submitted stock journal groups dropdown from either client cache or generate from DB data returned from server side.

    Parameters:
        reload (Boolean): Optional. True if clear cache is required. False by default.

    Returns:
        cache.get_cache (list): Submitted stock journal groups dropdown formed by stock journal groups DB table data.
    """
    from ..Utils.ClientCache import ClientDropdownCache
    cache = ClientDropdownCache(CacheKey.DD_SUBMITTED_JRN_GRP)
    if reload:
        cache.clear_cache()
    return cache.get_cache()

def generate_logging_level_dropdown():
    """
    Access application logging level dropdown from client side.

    Returns:
        list: Application logging level dropdown defined as static data in client Constants module.
    """
    return LoggingLevel.dropdown

def get_broker_dropdown_selected_item(broker_id):
    """
    Return a complete key based on a partial broker ID which is a part of the key in a dropdown list.

    Parameters:
        broker_id (string): The ID of the selected broker.

    Returns:
        selected_item (list): Complete key of the selected item in broker dropdown.
    """
    from ..Utils.ClientCache import ClientDropdownCache
    brokers_dropdown = ClientDropdownCache(CacheKey.DD_BROKER)
    selected_item = brokers_dropdown.get_complete_key(broker_id)
    return selected_item

def enable_search_time_datefield(interval_selection):
    """
    Enable or disable the "search time" (from, to) date field.

    Parameters:
        interval_selection (list): The selected value in list from the search interval dropdown.
        
    Returns:
        Boolean, Boolean: True for enable, false for disable.
    """
    from ..Utils.Constants import SearchInterval
    interval = interval_selection[0] if isinstance(interval_selection, (list, tuple)) else interval_selection
    return [True]*2 if interval == SearchInterval.INTERVAL_SELF_DEFINED else [False]*2

def set_search_time_datefield_value(interval_selection, date_from_value, date_to_value):
    """
    Set the "search time" (from, to) date field value.

    Parameters:
        interval_selection (list): The selected value in list from the search interval dropdown.
        date_from_value (date): The date to search from.
        date_from_to (date): The date to search to.
        
    Returns:
        String, String: Return original values provided in parameters if it's user defined, otherwise None.
    """
    from ..Utils.Constants import SearchInterval
    interval = interval_selection[0] if isinstance(interval_selection, (list, tuple)) else interval_selection
    return [date_from_value, date_to_value] if interval == SearchInterval.INTERVAL_SELF_DEFINED else [None] *2

def enable_broker_create_button(broker_name):
    """
    Enable or disable the broker action button (Create only).

    Parameters:
        broker_name (str): The to-be-created broker name.

    Returns:
        Boolean: True for enable, false for disable.
    """
    return False if broker_name in (None, '') or broker_name.isspace() else True

def enable_broker_update_delete_button(broker_selection):
    """
    Enable or disable the broker action buttons (Update and Delete only).

    Parameters:
        broker_selection (list): The selected value in list from the broker dropdown.
        
    Returns:
        Boolean, Boolean: True for enable, false for disable.
    """
    broker_id = broker_selection[0] if isinstance(broker_selection, (list, tuple)) else broker_selection
    return [False]*2 if broker_id in (None, '') or broker_id.isspace() else [True]*2

def set_selected_broker_fields(broker_selection):
    """
    Set the broker name and currency based on broker dropdown.

    Parameters:
        broker_selection (list): The selected value in list from the broker dropdown.
        
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
        broker_id = broker_selection
        broker_name, broker_ccy = [None] *2
    return [broker_id, broker_name, broker_ccy]

def visible_logging_panel():
    """
    Make the logging panel visible or invisible.

    Returns:
        Boolean: True for visible, false for invisible.
    """
    return True if anvil.app.environment.name in 'Dev' else False

@logger.log_function
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
        result (int): Successful update row count, otherwise None
    """
    from .. import Global
    from ..Utils.Constants import SearchInterval
    broker_id, _, _ = broker_dropdown_selected if isinstance(broker_dropdown_selected, (list, tuple)) else [broker_dropdown_selected, None, None]
    search_interval = interval_dropdown_selected[0] if isinstance(interval_dropdown_selected, (list, tuple)) else interval_dropdown_selected
    if search_interval != SearchInterval.INTERVAL_SELF_DEFINED:
        datefrom, dateto = [None, None]
    settings = Setting([Global.userid, broker_id, search_interval, datefrom, dateto, logging_level])
    result = anvil.server.call('upsert_settings', settings)
    logger.debug(f"Updated settings (Result: {result})\n{settings}")
    if not result:
        raise RuntimeError(f"Error occurs in proc_upsert_setting.")
    else:
        Global.settings = settings
        logger.set_level()
    return result

@logger.log_function
def change_broker(broker_dropdown_selected, broker_name, ccy_dropdown_selected):
    """
    Convert the fields from the form for creating or updating the broker change in backend.

    Parameters:
        broker_dropdown_selected (list): The selected value in list from the broker dropdown.
        broker_name (str): The selected or to-be-created broker name.
        ccy_dropdown_selected (list): The selected value in list from the currency dropdown.
        
    Returns:
        result (int): The ID of the newly created or row count of the updated broker, otherwise None.
    """
    from ..Utils.ClientCache import ClientDropdownCache
    cache = ClientDropdownCache(CacheKey.DD_BROKER)
    broker_id, _, _ = broker_dropdown_selected if isinstance(broker_dropdown_selected, (list, tuple)) else [broker_dropdown_selected, None, None]
    ccy = ccy_dropdown_selected[0] if isinstance(ccy_dropdown_selected, (list, tuple)) else ccy_dropdown_selected
    result = anvil.server.call('update_broker', broker_id, broker_name, ccy) if broker_id else \
        anvil.server.call('create_broker', broker_name, ccy)
    if not result:
        raise RuntimeError(f"Error occurs in create_broker or update_broker.")
    else:
        cache.clear_cache()
    return result

def delete_broker(broker_dropdown_selected):
    """
    Convert the fields from the form for deleting the broker change in backend.

    Parameters:
        broker_dropdown_selected (list): The selected value in list from the broker dropdown.
        
    Returns:
        result (int): Successful update row count, otherwise None.
    """
    from ..Utils.ClientCache import ClientDropdownCache
    cache = ClientDropdownCache(CacheKey.DD_BROKER)
    broker_id, _, _ = broker_dropdown_selected if isinstance(broker_dropdown_selected, (list, tuple)) else [broker_dropdown_selected, None, None]
    result = anvil.server.call('delete_broker', broker_id)
    if not result:
        raise RuntimeError(f"Error occurs in delete_broker.")
    else:
        cache.clear_cache()
    return result

@logger.log_function
def submit_journal_group(jrn_grp_dropdown_selected):
    """
    Convert the fields from the form for submitting the journal group change in backend.

    Parameters:
        jrn_grp_dropdown_selected (list): The selected value in list from the submitted journal group dropdown.
        
    Returns:
        result (int): Successful update row count, otherwise None.
    """
    from ..Entities.StockJournalGroup import StockJournalGroup
    from ..Utils.ClientCache import ClientDropdownCache
    cache = ClientDropdownCache(CacheKey.DD_SUBMITTED_JRN_GRP)
    jrn_grp_id, jrn_grp_name = jrn_grp_dropdown_selected if isinstance(jrn_grp_dropdown_selected, (list, tuple)) else [jrn_grp_dropdown_selected, None]
    jrn_grp = StockJournalGroup().set_id(jrn_grp_id).set_name(jrn_grp_name).set_submitted_status(False)
    result = anvil.server.call('submit_stock_journal_group', jrn_grp)
    if not result:
        raise RuntimeError(f"Error occurs in submit_stock_journal_group.")
    else:
        cache.clear_cache()
    return result

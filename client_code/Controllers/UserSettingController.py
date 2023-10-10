import anvil.server
import anvil.users

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

def generate_brokers_dropdown():
    """
    Access brokers dropdown from either client cache or generate from DB data returned from server side.

    Returns:
        brokers_dropdown (list): Brokers dropdown formed by partial brokers DB table data.
    """
    from ..Utils.ClientCache import ClientCache
    brokers_dropdown = ClientCache('generate_brokers_dropdown', None)
    if brokers_dropdown.is_empty():
        brokers_list = anvil.server.call('generate_brokers_simplified_list')
        new_dropdown = list((''.join([r['name'], ' [', r['ccy'], ']']), (r['broker_id'], r['name'], r['ccy'])) for r in brokers_list)
        brokers_dropdown.set_cache(new_dropdown)
    return brokers_dropdown.get_cache()

def get_broker_dropdown_selected_item(broker_id):
    """
    Return a complete key based on a partial broker ID which is a part of the key in a dropdown list.

    Returns:
        selected_item (list): Complete key of the selected item in broker dropdown.
    """
    from ..Utils.ClientCache import ClientCache
    brokers_dropdown = ClientCache('generate_brokers_dropdown', None)
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
    from ..Utils.Constants import ReportSearchMode
    interval = interval_selection[0] if isinstance(interval_selection, list) else interval_selection
    return [True] *2 if interval == ReportSearchMode.USER_DEFINED else [False] *2

def set_search_time_datefield_value(interval_selection, date_from_value, date_to_value):
    """
    Set the "search time" (from, to) date field value.

    Returns:
        String, String: Return original values provided in parameters if it's user defined, otherwise None.
    """
    from ..Utils.Constants import ReportSearchMode
    interval = interval_selection[0] if isinstance(interval_selection, list) else interval_selection
    return [date_from_value, date_to_value] if interval == ReportSearchMode.USER_DEFINED else [None] *2

def enable_broker_action_button(broker_selection):
    """
    Enable or disable the broker action buttons (Create, Update, Delete).

    Returns:
        Boolean, Boolean: True for enable, false for disable.
    """
    broker_id = broker_selection[0] if isinstance(broker_selection, list) else broker_selection
    return [False] *3 if broker_id in (None, '') or broker_id.isspace() else [True] *3

def set_selected_broker_fields(broker_selection):
    """
    Set the broker name and currency based on broker dropdown.

    Returns:
        broker_id (String): Selected broker ID.
        broker_name (String): Selected broker name, None instead if broker ID is none or empty.
        broker_ccy (String): Selected broker currency, None instead if broker ID is none or empty.
    """
    if isinstance(broker_selection, list):
        broker_id, broker_name, broker_ccy = broker_selection
        if broker_id in (None, '') or broker_id.isspace():
            broker_name, broker_ccy = [None] *2
    else:
        broker_name, broker_ccy = [None] *2
    return [broker_id, broker_name, broker_ccy]
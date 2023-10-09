import anvil.server
import anvil.users

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

def enable_search_time_datefield(self, interval_selection):
    """
    Enable or disable the "search time" (from, to) date field.

    Returns:
        Boolean, Boolean: True for enable, false for disable.
    """
    from ..Utils.Constants import ReportSearchMode
    interval = interval_selection[0] if isinstance(interval_selection, list) else interval_selection
    return [True] *2 if interval == ReportSearchMode.USER_DEFINED else [False] *2

def set_search_time_datefield_value(self, interval_selection, date_from_value, date_to_value):
    """
    Set the "search time" (from, to) date field value.

    Returns:
        String, String: Return original values provided in parameters if it's user defined, otherwise None.
    """
    from ..Utils.Constants import ReportSearchMode
    interval = interval_selection[0] if isinstance(interval_selection, list) else interval_selection
    return [date_from_value, date_to_value] if interval == ReportSearchMode.USER_DEFINED else [None] *2

def enable_broker_action_button(self, broker_selection):
    """
    Enable or disable the broker action buttons (Create, Update, Delete).

    Returns:
        Boolean, Boolean: True for enable, false for disable.
    """
    broker_id = broker_selection[0] if isinstance(broker_selection, list) else broker_selection
    return [False] *3 if broker_id in (None, '') or broker_id.isspace() else [True] *3

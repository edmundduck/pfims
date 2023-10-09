import anvil.server
import anvil.users

# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:

def enable_search_time_datefield(interval_selection):
    """
    Enable or disable the search time (from, to)

    Returns:
        setting (Setting): Setting object contains all user's setting.
    """
    from ..Utils.Constants import ReportSearchMode
    interval = interval_selection[0] if isinstance(interval_selection, list) else interval_selection
    return [True] *2 if interval != ReportSearchMode.USER_DEFINED else [False] *2
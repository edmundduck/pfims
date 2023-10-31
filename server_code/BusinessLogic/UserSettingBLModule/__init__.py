import anvil.server
from ...DataAccess import UserSettingDAModule
from ...SysProcess import LoggingModule

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.

logger = LoggingModule.ServerLogger()

@anvil.server.callable("proc_init_settings")
@logger.log_function
def proc_init_settings():
    """
    Consolidated process for setting form initialization.

    Returns:
        list: A list of all functions return required by the form initialization.
    """
    brokers = UserSettingDAModule.generate_brokers_simplified_list()
    search_interval = UserSettingDAModule.generate_search_interval_list()
    ccy = UserSettingDAModule.generate_currency_list()
    submitted_group_list = UserSettingDAModule.generate_submitted_journal_groups_list()
    return [brokers, search_interval, ccy, submitted_group_list]

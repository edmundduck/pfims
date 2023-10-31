import anvil.server
from ..DataAccess import StockTradingDAModule
from ..Entities.StockJournalGroup import StockJournalGroup
from ..SysProcess import LoggingModule

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.

logger = LoggingModule.ServerLogger()

@anvil.server.callable("proc_save_group_and_journals")
@logger.log_function
def proc_save_group_and_journals(jrn_grp, del_iid_list=None):
    """
    Consolidated process for saving stock journal group and journals.

    Parameters:
        jrn_grp (StockJournalGroup): The StockJournalGroup object of the selected stock journal group.
        del_iid_list (list): A list of IID (item ID) to be deleted, every journal has an IID.

    Returns:
        jrn_grp (StockJournalGroup): The StockJournalGroup object of the selected stock journal group.
        result_u (int): Successful update row count, otherwise None.
        result_d (int): Successful delete row count, otherwise None.
    """
    result_d = StockTradingDAModule.delete_journals(jrn_grp, del_iid_list)
    if jrn_grp.get_id():
        group_id = StockTradingDAModule.save_existing_stock_journal_group(jrn_grp)
    else:
        group_id = StockTradingDAModule.save_new_stock_journal_group(jrn_grp)
        if group_id is None or group_id <= 0:
            raise RuntimeError(f'ERROR: Fail to create new stock journal group {group_name}, aborting further update on journals.')
        jrn_grp = jrn_grp.set_id(group_id)
    result_u = StockTradingDAModule.upsert_journals(jrn_grp)
    return [jrn_grp, result_u, result_d]

@anvil.server.callable("init_cache_stock_trading_txn_detail")
@logger.log_function
def init_cache_stock_trading_txn_detail():
    from ..DataAccess import UserSettingDAModule
    broker_list = UserSettingDAModule.generate_brokers_simplified_list()
    jrn_list = StockTradingDAModule.generate_drafting_stock_journal_groups_list()
    return [broker_list, jrn_list]
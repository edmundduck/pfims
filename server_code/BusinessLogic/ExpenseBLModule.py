import anvil.server
from ..DataAccess import ExpenseDAModule
from ..Entities.Setting import Setting
from ..SysProcess import LoggingModule

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.

logger = LoggingModule.ServerLogger()

@anvil.server.callable("init_cache_expense_input")
@logger.log_function
def init_cache_expense_input():
    from ..CashMgtProcess import AccountModule, LabelModule
    exp_grp_list = ExpenseDAModule.generate_expense_groups_list()
    acct_list = AccountModule.generate_accounts_list()
    lbl_list = LabelModule.generate_labels_list()
    return exp_grp_list, acct_list, lbl_list
    
@anvil.server.callable("proc_select_expense_group")
@logger.log_function
def proc_select_expense_group(exp_grp):
    """
    Consolidated process for selecting one expense transaction group.

    Parameters:
        exp_grp (ExpenseTransactionGroup): The selected expense transaction group object.

    Returns:
        exp_grp (ExpenseTransactionGroup): The selected expense transaction group object filled with detail returned from the DB.
    """
    exp_grp = ExpenseDAModule.select_expense_group(exp_grp)
    tnx_list = ExpenseDAModule.select_transactions(exp_grp)
    exp_grp = exp_grp.set_transactions(tnx_list)
    return exp_grp

@anvil.server.callable("proc_change_expense_group")
@logger.log_function
def proc_change_expense_group(exp_grp, del_iid_list):
    """
    Consolidated process for making change on expense transaction group and transactions, including creation, update and deletion.

    Parameters:
        exp_grp (ExpenseTransactionGroup): The to-be-changed expense transaction group object.
        del_iid_list (list): A list of IID (item ID) to be deleted, every transaction has an IID.

    Returns:
        exp_grp (ExpenseTransactionGroup): The expense transaction group object updated with data from DB.
        result_d (int): Successful delete row count, otherwise None.
    """
    tab_id = ExpenseDAModule.update_expense_group(exp_grp) if exp_grp.get_id() else ExpenseDAModule.create_expense_group(exp_grp)
    if tab_id is None or tab_id <= 0:
        raise RuntimeError(f"ERROR occurs when creating or updating expense transaction group {exp_grp.get_name()}, aborting further update.")
    exp_grp = exp_grp.set_id(tab_id)
    updated_iid = ExpenseDAModule.upsert_transactions(exp_grp)

    # Replace all IID from the list of transactions.
    tnx_list = list(i.get_dict() for i in exp_grp.get_transactions())
    DL = {k: [dic[k] for dic in tnx_list] for k in tnx_list[0]}
    DL['iid'] = updated_iid
    updated_tnx_list = [dict(zip(DL, col)) for col in zip(*DL.values())]
    exp_grp = exp_grp.set_transactions(updated_tnx_list)

    result_d = ExpenseDAModule.delete_transactions(exp_grp, del_iid_list)
    return exp_grp, result_d

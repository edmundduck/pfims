import anvil.server
from .. import SystemProcess as sys
from ..DataAccess import ExpenseDAModule
from ..Entities.ExpenseTransaction import ExpenseTransaction
from ..Entities.Setting import Setting
from ..ServerUtils.LoggingModule import ServerLogger

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.

logger = ServerLogger()

@anvil.server.callable("init_cache_expense_input")
@logger.log_function
def init_cache_expense_input():
    from ..DataAccess import AccountDAModule, LabelDAModule
    exp_grp_list = ExpenseDAModule.generate_expense_groups_list()
    acct_list = AccountDAModule.generate_accounts_list()
    lbl_list = LabelDAModule.generate_labels_list()
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
    from ..Utils import Helper
    userid = sys.get_current_userid()
    exp_grp = ExpenseDAModule.select_expense_group(exp_grp)
    tnx_list = ExpenseDAModule.select_transactions(exp_grp)
    # Special handling to make keys found in expense_tbl_def all in upper case to match with client UI, server and DB definition
    # Without this the repeating panel can display none of the data returned from DB as the keys case from dict are somehow auto-lowered
    tnx_list = Helper.upper_dict_keys(tnx_list, ExpenseTransaction.get_data_transform_definition())
    exp_grp = exp_grp.set_transactions(list(ExpenseTransaction(r).set_user_id(userid) for r in tnx_list))
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
    # Validation
    if not exp_grp.is_valid():
        raise exp_grp.get_exception()

    tab_id = ExpenseDAModule.update_expense_group(exp_grp) if exp_grp.get_id() else ExpenseDAModule.create_expense_group(exp_grp)
    if tab_id is None or tab_id <= 0:
        raise RuntimeError(f"ERROR occurs when creating or updating expense transaction group {exp_grp.get_name()}, aborting further update.")
    exp_grp = exp_grp.set_id(tab_id)
    updated_iid = ExpenseDAModule.upsert_transactions(exp_grp)

    # Replace all IID from the list of transactions.
    tnx_list = list(i.get_dict() for i in exp_grp.get_transactions())
    DL = {k: [dic[k] for dic in tnx_list] for k in tnx_list[0]}
    DL['iid'] = list(r['iid'] for r in updated_iid)
    updated_tnx_list = [dict(zip(DL, col)) for col in zip(*DL.values())]
    exp_grp = exp_grp.set_transactions(updated_tnx_list)

    result_d = ExpenseDAModule.delete_transactions(exp_grp, del_iid_list)
    return exp_grp, result_d

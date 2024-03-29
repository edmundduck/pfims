import anvil.server
import pytest
from datetime import datetime
from ..DataAccess import ExpenseDAModule
from ..Entities.ExpenseTransactionGroup import ExpenseTransactionGroup
from ..Entities.ExpenseTransaction import ExpenseTransaction
from ..Entities.TestModule import TestModule
from .. import SystemProcess as sys

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.

class TestExpenseDAModule(TestModule):
    def get_test_object(self):
        return [
            ExpenseTransactionGroup({
                "userid": 365825345,
                "tab_id": 1,
                "tab_name": "Unit Test Expense Group",
                "submitted": True,
                "tab_create": datetime.strptime("2023-01-01", "%Y-%m-%d"),
                "tab_lastsave": None,
                "tab_submitted": None
            }),
            ExpenseTransaction({
                "iid": 1,
                "tab_id": 1,
                "trandate": datetime.strptime("2023-01-01", "%Y-%m-%d").date(),
                "account_id": 1,
                "amount": 100,
                "labels": [1],
                "remarks": "Unit test trx 1",
                "stmt_dtl": None
            })
        ]

    def get_sample_create_object(self):
        return ExpenseTransactionGroup({
            "userid": sys.get_current_userid(),
            "tab_id": None,
            "tab_name": "Unit Test NEW Exp Grp",
            "submitted": True,
            "tab_create": datetime.strptime("2023-12-29", "%Y-%m-%d").date(),
            "tab_lastsave": datetime.strptime("2023-12-30", "%Y-%m-%d").date(),
            "tab_submitted": datetime.strptime("2023-12-31", "%Y-%m-%d").date()
        })

    def test_generate_expense_groups_list(self):
        err = ["Retrieved expense group list is expected to be either list or tuple only."]
        try:
            assert isinstance(ExpenseDAModule.generate_expense_groups_list(), (list, tuple)), err[0]
        except AssertionError:
            return err[0]

    def test_select_expense_group(self):
        err = ["Retrieved expense group from database is not the same as expected."]
        exp_grp, _ = self.get_test_object()
        try:
            print(f"DEBUG: {exp_grp}")
            print(f"DEBUG: {ExpenseDAModule.select_expense_group(exp_grp)}")
            assert ExpenseDAModule.select_expense_group(exp_grp) == exp_grp, err[0]
        except AssertionError:
            return err[0]

    def test_select_transactions(self):
        err = ["Retrieved expense transactions from database are not the same as expected."]
        exp_grp, trx = self.get_test_object()
        try:
            print(f"DEBUG2: {trx}")
            print(f"DEBUG2: {ExpenseDAModule.select_transactions(exp_grp)}")
            assert ExpenseDAModule.select_transactions(exp_grp) == trx, err[0]
        except AssertionError:
            return err[0]

    # def test_create_delete_single_account(self):
    #     err = [
    #         "Created account returned from database does not match the originally defined attributes.", 
    #         "Created account remains in database after deletion.", 
    #         "Fail to delete the created account."
    #     ]
    #     acct = self.get_sample_create_object()
    #     new_id = AccountDAModule.create_account(acct)
    #     try:
    #         assert AccountDAModule.select_account(new_id) == acct.set_id(new_id), err[0]
    #     except AssertionError:
    #         return err[0]
    #     result = AccountDAModule.delete_account(acct.set_id(new_id))
    #     if result and result > 0:
    #         try:
    #             assert AccountDAModule.select_account(new_id) == None, err[1]
    #         except AssertionError:
    #             return err[1]
    #     else:
    #         return err[2]

    # def test_update_account(self):
    #     err = [
    #         "Update account returned from database does not match the originally defined attributes.", 
    #         "Fail to update the account."
    #     ]
    #     acct = self.get_test_object().set_name('Unittest')
    #     result = AccountDAModule.update_account(acct)
    #     if result and result > 0:
    #         try:
    #             assert AccountDAModule.select_account(acct.get_id()) == acct, err[0]
    #         except AssertionError:
    #             return err[0]
    #         AccountDAModule.update_account(acct.set_name('Account Test'))
    #     else:
    #         return err[1]

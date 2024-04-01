import anvil.server
import pytest
from datetime import datetime, timezone
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
                "submitted": False,
                "tab_create": datetime(2023, 1, 1, 0, 0, tzinfo=timezone.utc),
                "tab_lastsave": None,
                "tab_submitted": None
            }),
            ExpenseTransaction({
                "iid": 1,
                "tab_id": 1,
                "DTE": datetime.strptime("2023-01-01", "%Y-%m-%d").date(),
                "ACC": 1,
                "AMT": 100,
                "LBL": [1],
                "RMK": "Unit test trx 1",
                "STD": None
            })
        ]

    def get_sample_create_object(self):
        return ExpenseTransactionGroup({
            "userid": sys.get_current_userid(),
            "tab_id": None,
            "tab_name": "Unit Test NEW Exp Grp",
            "submitted": False,
            "tab_create": datetime(2023, 12, 29, 0, 0, tzinfo=timezone.utc),
            "tab_lastsave": datetime(2023, 12, 30, 0, 0, tzinfo=timezone.utc),
            "tab_submitted": None
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
            assert ExpenseDAModule.select_expense_group(exp_grp) == exp_grp, err[0]
        except AssertionError:
            return err[0]

    def test_select_transactions(self):
        err = [
            "Retrieved expense transactions from database are not the same as expected.",
            "Cannot retrieve any expense transactions."
        ]
        exp_grp, trx = self.get_test_object()
        try:
            assert ExpenseDAModule.select_transactions(exp_grp)[0] == trx, err[0]
        except AssertionError:
            return err[0]
        except IndexError:
            return err[1]

    def test_upsert_delete_transactions(self):
        err = [
            "Created transaction IID does not match which indicates upsert failure.",
            "Created transaction remains in database after deletion.",
            "Fail to delete the created transaction.",
            "Cannot retrieve transaction IID or the IID is corrupted."
        ]
        exp_grp, tnx = self.get_test_object()
        exp_grp = exp_grp.set_transactions(tnx)
        iid = ExpenseDAModule.upsert_transactions(exp_grp)
        try:
            assert iid[0]['iid'] == tnx.get_item_id(), err[0]
        except AssertionError:
            return err[0]
        except IndexError:
            return err[3]

        result = ExpenseDAModule.delete_transactions(exp_grp, [1])
        if result and result > 0:
            try:
                assert ExpenseDAModule.select_transactions(exp_grp) == [], err[1]
            except AssertionError:
                return err[1]
        else:
            return err[2]

    def test_create_delete_expense_group(self):
        err = [
            "Created expense group returned from database does not match the originally defined attributes.", 
            "Created expense group remains in database after deletion.", 
            "Fail to delete the created expense group."
        ]
        exp_grp = self.get_sample_create_object()
        new_id = ExpenseDAModule.create_expense_group(exp_grp)
        new_grp = exp_grp.set_id(new_id)
        print(f"DEBUG={ExpenseDAModule.select_expense_group(new_grp)}")
        print(f"DEBUG={exp_grp.set_id(new_id)}")
        try:
            assert ExpenseDAModule.select_expense_group(new_grp) == exp_grp.set_id(new_id), err[0]
        except AssertionError:
            return err[0]
        
        result = ExpenseDAModule.delete_expense_group(new_grp)
        if result and result > 0:
            try:
                assert ExpenseDAModule.select_expense_group(new_grp) == None, err[1]
            except AssertionError:
                return err[1]
        else:
            return err[2]

    def test_update_expense_group(self):
        err = [
            "Updated expense group returned from database does not match the originally defined attributes.", 
            "Fail to update the expense group."
        ]
        exp_grp, _ = self.get_test_object()
        exp_grp = exp_grp.set_name('Unit Test Expense Group Modified')
        result = ExpenseDAModule.update_expense_group(exp_grp)
        if result and result > 0:
            try:
                assert ExpenseDAModule.select_expense_group(exp_grp) == exp_grp, err[0]
            except AssertionError:
                return err[0]
            ExpenseDAModule.update_expense_group(exp_grp.set_name('Unit Test Expense Group'))
        else:
            return err[1]
        
    def test_submit_expense_group(self):
        pass

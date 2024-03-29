import anvil.server
import pytest
from datetime import datetime
from ..DataAccess import ExpenseDAModule
from ..Entities.ExpenseTransactionGroup import ExpenseTransactionGroup
from ..Entities.TestModule import TestModule
from .. import SystemProcess as sys

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.

class TestExpenseDAModule(TestModule):
    def get_test_object(self):
        return ExpenseTransactionGroup({
            "userid": '365825345',
            "tab_id": 1,
            "tab_name": "Account Test",
            "submitted": "GBP",
            "tab_create": datetime.strptime("2023-07-01", "%Y-%m-%d").date(),
            "tab_lastsave": datetime.strptime("2023-07-02", "%Y-%m-%d").date(),
            "tab_submitted": True
        })

    def get_sample_create_object(self):
        return Account({
            "userid": sys.get_current_userid(),
            "id": None,
            "name": "NEW ACCT for Test",
            "ccy": "GBP",
            "valid_from": None,
            "valid_to": None,
            "status": True

        })

    @anvil.server.callable
    def test_generate_expense_groups_list(self):
        err = ["Retrieved expense group list is expected to be either list or tuple only."]
        try:
            assert isinstance(ExpenseDAModule.generate_expense_groups_list(), (list, tuple)), err[0]
        except AssertionError:
            return err[0]

    @anvil.server.callable
    def test_select_expense_group(self):
        err = ["Retrieved expense group from database is not the same as expected."]
        exp_grp = self.get_test_object()
        try:
            assert ExpenseDAModule.select_expense_group(exp_grp.get_id()) == exp_grp, err[0]
        except AssertionError:
            return err[0]

    @anvil.server.callable
    def test_create_delete_single_account(self):
        err = [
            "Created account returned from database does not match the originally defined attributes.", 
            "Created account remains in database after deletion.", 
            "Fail to delete the created account."
        ]
        acct = self.get_sample_create_object()
        new_id = AccountDAModule.create_account(acct)
        try:
            assert AccountDAModule.select_account(new_id) == acct.set_id(new_id), err[0]
        except AssertionError:
            return err[0]
        result = AccountDAModule.delete_account(acct.set_id(new_id))
        if result and result > 0:
            try:
                assert AccountDAModule.select_account(new_id) == None, err[1]
            except AssertionError:
                return err[1]
        else:
            return err[2]

    @anvil.server.callable
    def test_update_account(self):
        err = [
            "Update account returned from database does not match the originally defined attributes.", 
            "Fail to update the account."
        ]
        acct = self.get_test_object().set_name('Unittest')
        result = AccountDAModule.update_account(acct)
        if result and result > 0:
            try:
                assert AccountDAModule.select_account(acct.get_id()) == acct, err[0]
            except AssertionError:
                return err[0]
            AccountDAModule.update_account(acct.set_name('Account Test'))
        else:
            return err[1]

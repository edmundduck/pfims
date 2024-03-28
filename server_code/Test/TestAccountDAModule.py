import anvil.server
import pytest
from datetime import datetime
from ..DataAccess import AccountDAModule
from ..Entities.Account import Account
from ..Entities.TestModule import TestModule
from .. import SystemProcess as sys

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.

class TestAccountDAModule(TestModule):
    def get_test_object(self):
        return Account({
            "userid": 365825345,
            "id": 1,
            "name": "Account Test",
            "ccy": "GBP",
            "valid_from": datetime.strptime("2023-07-01", "%Y-%m-%d").date(),
            "valid_to": datetime.strptime("2023-07-02", "%Y-%m-%d").date(),
            "status": True
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
    def test_generate_accounts_list(self):
        try:
            assert isinstance(AccountDAModule.generate_accounts_list(), (list, tuple)), "Retrieved account from database is not the same as expected."
        except AssertionError:
            return "Retrieved account list is neither a list nor a tuple."

    @anvil.server.callable
    def test_select_account(self):
        acct = self.get_test_object()
        try:
            assert AccountDAModule.select_account(acct.get_id()) == acct, "Retrieved account from database is not the same as expected."
        except AssertionError:
            return "Retrieved account from database is not the same as expected."

    @anvil.server.callable
    def test_create_delete_single_account(self):
        err = ["Created account returned from database does not match the originally defined attributes.", "Created account remains in database after deletion.", "Fail to delete the created account."]
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
        err = ["Update account returned from database does not match the originally defined attributes.", "Fail to update the account."]
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

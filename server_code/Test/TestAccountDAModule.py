import anvil.server
import pytest
from ..DataAccess import AccountDAModule
from ..Entities.Account import Account
from ..Entities.TestModule import TestModule
from ..Utils import MockUpData

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.

class TestAccountDAModule(TestModule):
    def test_generate_accounts_list(self):
        err = ["Retrieved account list is expected to be either list or tuple only."]
        try:
            assert isinstance(AccountDAModule.generate_accounts_list(), (list, tuple)), err[0]
        except AssertionError:
            return err[0]

    def test_select_account(self):
        err = ["Retrieved account from database is not the same as expected."]
        acct = Account(MockUpData.get_first_element(MockUpData.get_mockup_account)())
        try:
            assert AccountDAModule.select_account(acct.get_id()) == acct, err[0]
        except AssertionError:
            return err[0]

    def test_create_delete_single_account(self):
        err = [
            "Created account returned from database does not match the originally defined attributes.", 
            "Created account remains in database after deletion.", 
            "Fail to delete the created account."
        ]
        acct = Account(MockUpData.get_first_element(MockUpData.get_new_mockup_account)())
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

    def test_update_account(self):
        err = [
            "Updated account returned from database does not match the originally defined attributes.", 
            "Fail to update the account."
        ]
        acct = Account(MockUpData.get_first_element(MockUpData.get_mockup_account)()).set_name('Unittest')
        result = AccountDAModule.update_account(acct)
        if result and result > 0:
            try:
                assert AccountDAModule.select_account(acct.get_id()) == acct, err[0]
            except AssertionError:
                return err[0]
            AccountDAModule.update_account(acct.set_name('Account Test'))
        else:
            return err[1]

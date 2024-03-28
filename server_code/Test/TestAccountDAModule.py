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
            "userid": sys.get_current_userid(),
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
        assert (result := isinstance(AccountDAModule.generate_accounts_list(), (list, tuple)))
        return result

    @anvil.server.callable
    def test_select_account(self):
        acct = self.get_test_object()
        assert (result := AccountDAModule.select_account(acct.get_id()) == acct)
        return result

    @anvil.server.callable
    def test_create_delete_single_account(self):
        acct = self.get_sample_create_object()
        new_id = AccountDAModule.create_account(acct)
        assert (result := AccountDAModule.select_account(new_id) == acct.set_id(new_id))
        result = AccountDAModule.delete_account(acct.set_id(new_id))
        if result and result > 0:
            assert (result_del := AccountDAModule.select_account(new_id) == None)
            return all([result, result_del])
        else:
            assert False

    @anvil.server.callable
    def test_update_account(self):
        acct = self.get_test_object().set_name('Unittest')
        result = AccountDAModule.update_account(acct)
        if result and result > 0:
            assert (result := AccountDAModule.select_account(acct.get_id()) == acct)
            AccountDAModule.update_account(acct.set_name('EMPTY'))
            return result
        else:
            assert False

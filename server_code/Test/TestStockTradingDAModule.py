import anvil.server
import pytest
from ..DataAccess import StockTradingDAModule
from ..Entities.StockJournalGroup import StockJournalGroup
from ..Entities.TestModule import TestModule
from ..Utils import MockUpData

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.

class TestStockTradingDAModule(TestModule):
    def test_generate_drafting_stock_journal_groups_list(self):
        err = ["Generated drafting stock journal group list does not match."]
        jrn_grp_list = [ dict(x) for x in StockTradingDAModule.generate_drafting_stock_journal_groups_list()]
        test_list = MockUpData.get_mockup_stock_journal_group().copy()
        try:
            assert isinstance(jrn_grp_list, (list, tuple)), err[0]
            for jrn_grp in jrn_grp_list:
                test_list.remove(jrn_grp)
                if len(test_list) == 0: break
            assert len(test_list) == 0, err[0]
        except ValueError:
            return err[0]
        except AssertionError:
            return err[0]

    def test_select_stock_journal_group(self):
        err = ["Retrieved stock journal group from database is not the same as expected."]
        jrn_grp = StockJournalGroup(MockUpData.get_first_element(MockUpData.get_mockup_stock_journal_group)())
        try:
            assert StockTradingDAModule.select_stock_journal_group(jrn_grp.get_id()) == jrn_grp, err[0]
        except AssertionError:
            return err[0]

    def test_select_stock_journals(self):
        err = ["Retrieved stock journals from database are not the same as expected."]
        jrn_grp = StockJournalGroup(MockUpData.get_first_element(MockUpData.get_mockup_stock_journal_group)())
        try:
            assert StockTradingDAModule.select_stock_journal_group(jrn_grp.get_id()) == jrn_grp, err[0]
        except AssertionError:
            return err[0]

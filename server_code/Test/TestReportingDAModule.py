import anvil.server
import pytest
from ..DataAccess import ReportingDAModule
from ..Entities.TestModule import TestModule
from ..Utils import MockUpData

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.

class TestReportingDAModule(TestModule):
    def test_select_journals(self):
        err = ["Retrieved journals (without symbols) from database are not the same as expected."]
        coded_cases = MockUpData.get_mockup_stock_journals()
        jrns_db = ReportingDAModule.select_journals(MockUpData.get_mockup_selected_start_date(), MockUpData.get_mockup_selected_end_date())
        test_list = coded_cases.copy()
        try:
            for jrn in jrns_db:
                test_list.remove(dict(jrn))
            assert len(test_list) == 0, err[0]
        except ValueError:
            return err[0]
        except AssertionError:
            return err[0]

    def test_select_journals_with_symbol(self):
        err = ["Retrieved journals (with symbols) from database are not the same as expected."]
        coded_cases = MockUpData.get_mockup_stock_journals()
        jrns_db = ReportingDAModule.select_journals(MockUpData.get_mockup_selected_start_date(), MockUpData.get_mockup_selected_end_date(), MockUpData.get_mockup_selected_symbol())
        test_list = list(filter((lambda x: x.get("symbol") in MockUpData.get_mockup_selected_symbol()), coded_cases))
        try:
            for jrn in jrns_db:
                test_list.remove(dict(jrn))
            assert len(test_list) == 0, err[0]
        except ValueError:
            return err[0]
        except AssertionError:
            return err[0]

    def test_select_transactions_filter_by_labels(self):
        err = ["Retrieved transactions (without labels) from database are not the same as expected."]
        coded_cases = MockUpData.get_mockup_transactions()
        tnxs_db = ReportingDAModule.select_transactions_filter_by_labels(MockUpData.get_mockup_selected_start_date(), MockUpData.get_mockup_selected_end_date())
        test_list = coded_cases.copy()
        try:
            for tnx in tnxs_db:
                test_list.remove(dict(tnx))
            assert len(test_list) == 0, err[0]
        except ValueError:
            return err[0]
        except AssertionError:
            return err[0]

    def test_select_transactions_filter_by_labels_with_label(self):
        err = ["Retrieved transactions (with labels) from database are not the same as expected."]
        coded_cases = MockUpData.get_mockup_transactions()
        tnxs_db = ReportingDAModule.select_transactions_filter_by_labels(MockUpData.get_mockup_selected_start_date(), MockUpData.get_mockup_selected_end_date(), MockUpData.get_mockup_selected_labels())
        test_list = list(filter(lambda x: set(x.get("LBL")).intersection(MockUpData.get_mockup_selected_labels()), coded_cases))
        try:
            for tnx in tnxs_db:
                test_list.remove(dict(tnx))
            assert len(test_list) == 0, err[0]
        except ValueError:
            return err[0]
        except AssertionError:
            return err[0]

    def test_select_summed_total_per_labels(self):
        err = ["Retrieved summed total (without labels) from database is not the same as expected."]
        coded_cases = MockUpData.get_mockup_labels_summed_total()
        tnxs_db = ReportingDAModule.select_summed_total_per_labels(MockUpData.get_mockup_selected_start_date(), MockUpData.get_mockup_selected_end_date())

        try:
            for tnx in tnxs_db:
                for c in coded_cases:
                    if tnx.get("LBL") == c.get("LBL"):
                        assert tnx.get("AMT") == c.get("AMT")
        except AssertionError:
            return err[0]

    def test_select_balance_per_account(self):
        err = ["Retrieved balance (without accounts) from database is not the same as expected."]
        coded_cases = MockUpData.get_mockup_accounts_balance()
        tnxs_db = ReportingDAModule.select_balance_per_account(MockUpData.get_mockup_selected_start_date(), MockUpData.get_mockup_selected_end_date())

        try:
            for tnx in tnxs_db:
                for c in coded_cases:
                    if tnx.get("ACC") == c.get("ACC"):
                        assert tnx.get("AMT") == c.get("AMT")
        except AssertionError:
            return err[0]

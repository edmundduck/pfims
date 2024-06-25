import anvil.server
import pytest
from ..DataAccess import UserSettingDAModule
from ..Entities.Setting import Setting
from ..Entities.TestModule import TestModule
from ..Utils import MockUpData

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.

class TestUserSettingDAModule(TestModule):
    def test_select_settings(self):
        err = ["Retrieved user setting from database is not the same as expected."]
        try:
            assert UserSettingDAModule.select_settings() == Setting(MockUpData.get_mockup_setting()), err[0]
        except AssertionError:
            return err[0]

    def test_generate_brokers_simplified_list(self):
        err = ["Retrieved brokers list is expected to be either list or tuple only."]
        try:
            assert isinstance(UserSettingDAModule.generate_brokers_simplified_list(), (list, tuple)), err[0]
        except AssertionError:
            return err[0]

    def test_generate_currency_list(self):
        err = ["Retrieved currency list is expected to be either list or tuple only."]
        try:
            assert isinstance(UserSettingDAModule.generate_currency_list(), (list, tuple)), err[0]
        except AssertionError:
            return err[0]

    def test_generate_submitted_journal_groups_list(self):
        err = ["Retrieved submitted journal groups list is expected to be either list or tuple only."]
        try:
            assert isinstance(UserSettingDAModule.generate_submitted_journal_groups_list(), (list, tuple)), err[0]
        except AssertionError:
            return err[0]

    def test_generate_search_interval_list(self):
        err = ["Retrieved search interval list is expected to be either list or tuple only."]
        try:
            assert isinstance(UserSettingDAModule.generate_search_interval_list(), (list, tuple)), err[0]
        except AssertionError:
            return err[0]

    def test_upsert_settings(self):
        err = [
            "Fail to update to the new settings.",
            "Fail to update back to the original settings."
        ]
        new_setting = Setting(MockUpData.get_new_mockup_setting())
        UserSettingDAModule.upsert_settings(new_setting)
        try:
            assert UserSettingDAModule.select_settings() == new_setting, err[0]
        except AssertionError:
            return err[0]

        original_setting = Setting(MockUpData.get_mockup_setting())
        UserSettingDAModule.upsert_settings(original_setting)
        try:
            assert UserSettingDAModule.select_settings() == original_setting, err[0]
        except AssertionError:
            return err[0]

    def test_create_delete_broker(self):
        err = [
            "Created broker returned from database does not match the originally defined attributes.",
            "Created broker remains in database after deletion.",
            "Fail to delete the created broker."
        ]
        selected_broker = MockUpData.get_new_mockup_broker()
        new_broker_id = UserSettingDAModule.create_broker(selected_broker['name'], selected_broker['ccy'])
        new_broker = {
            "broker_id": new_broker_id,
            "name": MockUpData.get_new_mockup_broker()['name'],
            "ccy": MockUpData.get_new_mockup_broker()['ccy']
        }
        try:
            assert any(new_broker == dict(x) for x in UserSettingDAModule.generate_brokers_simplified_list()), err[0]
        except AssertionError:
            return err[0]
        result = UserSettingDAModule.delete_broker(new_broker_id)
        if result and result > 0:
            try:
                assert all(new_broker != dict(x) for x in UserSettingDAModule.generate_brokers_simplified_list()), err[1]
            except AssertionError:
                return err[1]
        else:
            return err[2]

    def test_update_broker(self):
        err = [
            "Updated broker returned from database does not match the originally defined attributes."
        ]
        broker = MockUpData.get_first_element(MockUpData.get_mockup_broker)()
        broker['ccy'] = "HKD"
        try:
            assert UserSettingDAModule.update_broker(broker['broker_id'], broker['name'], broker['ccy']) == 1, err[0]
        except AssertionError:
            return err[0]
        UserSettingDAModule.update_broker(broker['broker_id'], broker['name'], MockUpData.get_first_element(MockUpData.get_mockup_broker)()['ccy'])

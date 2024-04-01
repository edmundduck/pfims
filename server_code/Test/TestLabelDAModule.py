import anvil.server
import pytest
from ..DataAccess import LabelDAModule
from ..Entities.Label import Label
from ..Entities.TestModule import TestModule
from .. import SystemProcess as sys

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.

class TestLabelDAModule(TestModule):
    def get_test_object(self):
        return Label({
            "userid": 365825345,
            "id": 1,
            "name": "Label Unit Test",
            "status": True,
            "keywords": None
        })

    def get_sample_create_object(self):
        return Label({
            "userid": sys.get_current_userid(),
            "id": None,
            "name": "Unit Test Label New",
            "status": True,
            "keywords": None
        })

    def test_generate_labels_list(self):
        err = ["Retrieved label list is expected to be either list or tuple only."]
        try:
            assert isinstance(LabelDAModule.generate_labels_list(), (list, tuple)), err[0]
        except AssertionError:
            return err[0]

    def test_generate_labels_mapping_action_list(self):
        err = ["Retrieved labels mapping action list is expected to be either list or tuple only."]
        try:
            assert isinstance(LabelDAModule.generate_labels_mapping_action_list(), (list, tuple)), err[0]
        except AssertionError:
            return err[0]

    def test_select_label(self):
        err = ["Retrieved label from database is not the same as expected."]
        lbl = self.get_test_object()
        try:
            assert LabelDAModule.select_label(lbl.get_id()) == lbl, err[0]
        except AssertionError:
            return err[0]

    def test_create_delete_single_label(self):
        err = [
            "Created label returned from database does not match the originally defined attributes.", 
            "Created label remains in database after deletion.", 
            "Fail to delete the created label.", 
            "Fail to create a label for testing."
        ]
        lbl = self.get_sample_create_object()
        new_id = LabelDAModule.create_label(lbl)
        try:
            assert LabelDAModule.select_label(new_id[0]) == lbl.set_id(new_id[0]), err[0]
        except AssertionError:
            return err[0]
        except IndexError:
            return err[3]
        result = LabelDAModule.delete_label(lbl.set_id(new_id[0]))
        if result and result > 0:
            try:
                assert LabelDAModule.select_label(new_id[0]) == None, err[1]
            except AssertionError:
                return err[1]
        else:
            return err[2]

    def test_update_label(self):
        err = [
            "Updated account returned from database does not match the originally defined attributes.", 
            "Fail to update the account."
        ]
        lbl = self.get_test_object().set_keywords('Unittest')
        result = LabelDAModule.update_label(lbl)
        if result and result > 0:
            try:
                assert LabelDAModule.select_label(lbl.get_id()) == lbl, err[0]
            except AssertionError:
                return err[0]
            LabelDAModule.update_label(lbl.set_keywords(''))
        else:
            return err[1]

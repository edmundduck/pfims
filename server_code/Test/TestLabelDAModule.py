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
            "userid": '365825345',
            "id": 1,
            "name": "Label Unit Test",
            "status": True,
            "keywords": ''
        })

    def get_sample_create_object(self):
        return Label({
            "userid": sys.get_current_userid(),
            "id": None,
            "name": "Unit Test Label New",
            "status": True,
            "keywords": ''
        })

    @anvil.server.callable
    def test_generate_labels_list(self):
        err = ["Retrieved label list is expected to be either list or tuple only."]
        try:
            assert isinstance(LabelDAModule.generate_labels_list(), (list, tuple)), err[0]
        except AssertionError:
            return err[0]

    @anvil.server.callable
    def test_generate_labels_mapping_action_list(self):
        err = ["Retrieved labels mapping action list is expected to be either list or tuple only."]
        try:
            assert isinstance(LabelDAModule.generate_labels_mapping_action_list(), (list, tuple)), err[0]
        except AssertionError:
            return err[0]

    @anvil.server.callable
    def test_select_label(self):
        err = ["Retrieved label from database is not the same as expected."]
        lbl = self.get_test_object()
        try:
            assert LabelDAModule.select_label(lbl.get_id()) == lbl, err[0]
        except AssertionError:
            return err[0]

    @anvil.server.callable
    def test_create_delete_single_label(self):
        lbl = self.get_sample_create_object()
        new_id = LabelDAModule.create_label(lbl)
        try:
            if new_id:
                new_id = new_id[0]
        except IndexError:
            pass
        assert (result := LabelDAModule.select_label(new_id) == lbl.set_id(new_id))
        result = LabelDAModule.delete_label(lbl.set_id(new_id))
        if result and result > 0:
            assert (result_del := LabelDAModule.select_label(new_id) == None)
            return all([result, result_del])
        else:
            assert False

    @anvil.server.callable
    def test_update_label(self):
        lbl = self.get_test_object().set_keywords('Unittest')
        result = LabelDAModule.update_label(lbl)
        if result and result > 0:
            assert (result := LabelDAModule.select_label(lbl.get_id()) == lbl)
            LabelDAModule.update_label(lbl.set_keywords(''))
            return result
        else:
            assert False

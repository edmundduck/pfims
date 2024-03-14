import anvil.server
import pytest
from ..DataAccess import LabelDAModule
from ..Entities.Label import Label
from .. import SystemProcess as sys

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.

def get_test_object():
    return Label({
        "userid": sys.get_current_userid(),
        "id": 1,
        "name": "膳食",
        "status": True,
        "keywords": ''
    })

def get_sample_create_object():
    return Label({
        "userid": sys.get_current_userid(),
        "id": None,
        "name": "Unit Test Label 1",
        "status": True,
        "keywords": ''
    })

@anvil.server.callable
def test_generate_labels_list():
    assert (result := isinstance(LabelDAModule.generate_labels_list(), (list, tuple)))
    return result

@anvil.server.callable
def test_generate_labels_mapping_action_list():
    assert (result := isinstance(LabelDAModule.generate_labels_mapping_action_list(), (list, tuple)))
    return result

@anvil.server.callable
def test_select_label():
    lbl = get_test_object()
    assert (result := LabelDAModule.select_label(lbl.get_id()) == lbl)
    return result

@anvil.server.callable
def test_create_delete_single_label():
    lbl = get_sample_create_object()
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
def test_update_label():
    lbl = get_test_object().set_keywords('Unittest')
    result = LabelDAModule.update_label(lbl)
    if result and result > 0:
        assert (result := LabelDAModule.select_label(lbl.get_id()) == lbl)
        LabelDAModule.update_label(lbl.set_keywords(''))
        return result
    else:
        assert False

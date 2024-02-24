import anvil.server
import pytest
from ..DataAccess import LabelDAModule
from ..Entities.Label import Label

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.

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
    test_id = 1
    # assert ()
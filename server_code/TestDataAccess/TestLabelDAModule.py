import anvil.server
import pytest
from ..DataAccess import LabelDAModule

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.

@anvil.server.callable
def test_generate_labels_list_normal_case():
    assert (result := isinstance(LabelDAModule.generate_labels_list(), (list, tuple)))
    return result

def 
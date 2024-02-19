import anvil.server
import pytest
from ..DataAccess import LabelDAModule

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.

def test_generate_labels_list_normal_case():
    assert isinstance(LabelDAModule.generate_labels_list(), (list, tuple))
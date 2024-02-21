from ._anvil_designer import UnitTestMainFormTemplate
from anvil import *
import anvil.server

class UnitTestMainForm(UnitTestMainFormTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        self.test_item_1.title = "TestLabelDAModule"
        sefl.test_item_1.test_function = "test_generate_labels_list_normal_case"

    def test_item_1_click(self, **event_args):
        

from ._anvil_designer import UnitTestMainFormTemplate
from anvil import *
import anvil.server

class UnitTestMainForm(UnitTestMainFormTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.

    def button_case_1_click(self, **event_args):
        """This method is called when the button is clicked"""
        anvil.server.call('test_generate_labels_list_normal_case')

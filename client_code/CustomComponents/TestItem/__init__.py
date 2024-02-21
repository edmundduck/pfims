from ._anvil_designer import TestItemTemplate
from anvil import *
import anvil.server

class TestItem(TestItemTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        self.label.text = self.title

    def button_run_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.result_success = anvil.server.call(self.test_function)
        self.result.text = f"Success ({self.result_success})"

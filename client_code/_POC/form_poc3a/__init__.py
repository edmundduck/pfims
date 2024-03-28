from ._anvil_designer import form_poc3aTemplate
from anvil import *
import anvil.server
from ...Utils.Validation import Validator

class form_poc3a(form_poc3aTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        self.repeating_panel_1.items = [{} for i in range(2)]

    def button_1_click(self, **event_args):
        """This method is called when the button is clicked"""
        v = Validator()
        v.display_when_invalid(self.valerror)
        v.require_text_field((row for row in self.repeating_panel_1.items['text']), self.valerror1, False)

    def button_2_click(self, **event_args):
        """This method is called when the button is clicked"""
        pass

from ._anvil_designer import form_poc3aTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ...Utils.Validation import Validator
from ...Utils.Logger import trace, debug, info, warning, error, critical

class form_poc3a(form_poc3aTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        self.repeating_panel_1.items = [{} for i in range(2)]
        error.log("xx")
        error.log("level=", anvil.server.call('get_user_logging_level'))
        error.log("brokers=", anvil.server.call('select_brokers'))
        error.log("level=", anvil.server.call('get_user_logging_level'))
        error.log("yy")

    def button_1_click(self, **event_args):
        """This method is called when the button is clicked"""
        v = Validator()
        v.display_when_invalid(self.valerror)
        v.require_text_field((row for row in self.repeating_panel_1.items['text']), self.valerror1, False)
        # v.highlight_when_invalid(self.text_box_1, 'rgb(245,135,200)', self.text_box_1.background)

    def button_2_click(self, **event_args):
        """This method is called when the button is clicked"""
        pass

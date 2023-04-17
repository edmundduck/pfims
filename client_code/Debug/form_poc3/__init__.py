from ._anvil_designer import form_poc3Template
from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class form_poc3(form_poc3Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        self.repeating_panel_1.items = [{} for i in range(2)]

    def button_1_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.repeating_panel_1.raise_event_on_children('x-validate')

    def button_2_click(self, **event_args):
        """This method is called when the button is clicked"""
        pass



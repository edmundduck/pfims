from ._anvil_designer import form_poc3Template
from anvil import *
import anvil.server
from ...Utils.Logger import ClientLogger

class form_poc3(form_poc3Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        self.logger = ClientLogger()

        # Any code you write here will run before the form opens.
        self.repeating_panel_1.items = [{} for i in range(2)]

    def button_1_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.repeating_panel_1.raise_event_on_children('x-validate')

    def button_2_click(self, **event_args):
        """This method is called when the button is clicked"""
        for c in self.data_grid_1.columns:
            self.logger.debug(c['data_key'])
        # column = [c for c in self.data_grid_1.columns if c['data_key'] == 'column_2'][0]
        column = self.data_grid_1.columns[0]
        self.data_grid_1.columns.remove(column)
        self.data_grid_1.columns = self.data_grid_1.columns



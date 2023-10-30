from ._anvil_designer import TransactionReportFormTemplate
from anvil import *

class TransactionReportForm(TransactionReportFormTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
    
        # Any code you write here will run when the form opens.
        self.data_grid.rows_per_page = self.dropdown_displayrow.selected_value

    def dropdown_displayrow_change(self, **event_args):
        """This method is called when an item is selected"""
        self.data_grid.rows_per_page = self.dropdown_displayrow.selected_value

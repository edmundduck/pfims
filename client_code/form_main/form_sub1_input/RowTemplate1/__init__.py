from ._anvil_designer import RowTemplate1Template
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class RowTemplate1(RowTemplate1Template):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    self.input_data_panel_readonly.item['symbol'] = "ABC"

  def input_button_edit_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.input_data_panel_readonly.visible = False
    self.input_data_panel_editable.visible = True

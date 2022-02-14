from ._anvil_designer import form_poc_mainTemplate
from anvil import *
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..form_poc1 import form_poc1
from ..form_poc2 import form_poc2
from ..form_poc3 import form_poc3
from ... import global_var

class form_poc_main(form_poc_mainTemplate):
  subform = None
  
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.

  def button_select_click(self, **event_args):
    """This method is called when the button is clicked"""
    if self.radio_button_1.selected is True:
      self.test_column_panel.add_component(form_poc1())
    elif self.radio_button_2.selected is True:
      self.test_column_panel.add_component(form_poc2())
    elif self.radio_button_3.selected is True:
      self.test_column_panel.add_component(form_poc3())

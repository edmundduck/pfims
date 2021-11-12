from ._anvil_designer import form_testaTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..form_testb import form_testb

class form_testa(form_testaTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.

  def test_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    form_testb().label_1.text = "Click from FORM A"
    self.label_1.text = "Can form B do the same?"
    


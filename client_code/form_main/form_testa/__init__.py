from ._anvil_designer import form_testaTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ..form_testb import form_testb
from ..form_testc import form_testc
from ..form_lv2_tranx_list import form_lv2_tranx_list
from ... import global_var

class form_testa(form_testaTemplate):
  subform = None
  
  def __init__(self, form_name, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    if form_name == 'form_a':
      self.subform = form_testb()
      self.test_column_panel.add_component(self.subform)
    elif form_name == 'form_b':
      self.subform = form_testc()
      self.test_column_panel.add_component(self.subform)
    else:
      print(global_var.form_lv2_tranx_list())

  def test_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.subform.label_1.text = 'Changed'

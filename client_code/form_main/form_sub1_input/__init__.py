from ._anvil_designer import form_sub1_inputTemplate
from anvil import *

class form_sub1_input(form_sub1_inputTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.